from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import yaml


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from src.client_atlas import requete_get, requete_post, verifier_connexion  # noqa: E402


METADATA_DIR = BASE_DIR / "metadata"
TECHNICAL_METADATA_PATH = METADATA_DIR / "metadonnees_extraites.json"
TABLE_METADATA_PATH = METADATA_DIR / "metadonnees_tables.yaml"
COLUMN_METADATA_PATH = METADATA_DIR / "classifications_colonnes.yaml"


def lire_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"fichier introuvable: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def lire_yaml(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"fichier introuvable: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def qualified_table(nom_table: str) -> str:
    return f"datalake://local/{nom_table}@TER"


def qualified_colonne(nom_table: str, nom_colonne: str) -> str:
    return f"datalake://local/{nom_table}/{nom_colonne}@TER"


def entite_existe(type_name: str, qualified_name: str) -> bool:
    try:
        requete_get(
            f"entity/uniqueAttribute/type/{type_name}",
            params={"attr:qualifiedName": qualified_name},
        )
        return True
    except RuntimeError as erreur:
        if "404" in str(erreur) or "Not Found" in str(erreur):
            return False
        raise


def creer_entites(entites: list[dict]) -> int:
    if not entites:
        return 0

    try:
        requete_post("entity/bulk", {"entities": entites})
    except RuntimeError as erreur:
        if "timed out" not in str(erreur):
            raise

        print("Atlas est lent, verification des entites")
        if not attendre_creation(entites):
            raise

    return len(entites)


def attendre_creation(entites: list[dict]) -> bool:
    for _ in range(12):
        manquantes = [
            entite
            for entite in entites
            if not entite_existe(
                entite["typeName"],
                entite["attributes"]["qualifiedName"],
            )
        ]
        if not manquantes:
            return True
        time.sleep(10)
    return False


def construire_table(table_technique: dict, table_metier: dict) -> dict:
    nom_table = table_technique["nom_table"]
    return {
        "typeName": "datalake_table",
        "attributes": {
            "name": nom_table,
            "qualifiedName": qualified_table(nom_table),
            "description": table_metier.get("description", ""),
            "domaine": table_metier.get("domain", ""),
            "proprietaire": table_metier.get("owner", ""),
            "chemin": table_technique.get("chemin_fichier", ""),
            "format_source": table_metier.get("source_format", "csv"),
            "format_cible": table_technique.get("format", table_metier.get("target_format", "")),
            "niveau_sensibilite": table_metier.get("sensitivity_level", ""),
            "statut_qualite": table_metier.get("quality_status", ""),
            "nombre_lignes": table_technique.get("nombre_lignes", 0),
            "fichier_source": f"data/raw/{nom_table}.csv",
        },
    }


def construire_colonne(nom_table: str, colonne_technique: dict, colonne_metier: dict) -> dict:
    nom_colonne = colonne_technique["nom"]
    return {
        "typeName": "datalake_column",
        "attributes": {
            "name": nom_colonne,
            "qualifiedName": qualified_colonne(nom_table, nom_colonne),
            "table_name": nom_table,
            "type_donnee": colonne_technique.get("type", colonne_metier.get("data_type", "")),
            "description": colonne_metier.get("description", ""),
            "est_sensible": bool(colonne_metier.get("is_sensitive", False)),
            "concerne_rgpd": bool(colonne_metier.get("rgpd_relevant", False)),
        },
    }


def preparer_table(table_technique: dict, table_metier: dict) -> dict | None:
    entite = construire_table(table_technique, table_metier)
    qualified_name = entite["attributes"]["qualifiedName"]

    if entite_existe("datalake_table", qualified_name):
        print(f"Table deja presente: {table_technique['nom_table']}")
        return None

    return entite


def preparer_colonnes(table_technique: dict, colonnes_metier: dict) -> list[dict]:
    nom_table = table_technique["nom_table"]
    entites = []

    for colonne_technique in table_technique.get("colonnes", []):
        nom_colonne = colonne_technique["nom"]
        colonne_metier = colonnes_metier.get(nom_colonne, {})
        entite = construire_colonne(nom_table, colonne_technique, colonne_metier)
        qualified_name = entite["attributes"]["qualifiedName"]

        if entite_existe("datalake_column", qualified_name):
            print(f"Colonne deja presente: {nom_table}.{nom_colonne}")
            continue

        entites.append(entite)

    return entites


def afficher_creations(entites: list[dict]) -> None:
    for entite in entites:
        attributs = entite["attributes"]
        if entite["typeName"] == "datalake_table":
            print(f"Table creee: {attributs['name']}")
        else:
            print(f"Colonne creee: {attributs['table_name']}.{attributs['name']}")


def main() -> None:
    try:
        verifier_connexion()
        metadonnees_techniques = lire_json(TECHNICAL_METADATA_PATH)
        metadonnees_tables = lire_yaml(TABLE_METADATA_PATH)
        metadonnees_colonnes = lire_yaml(COLUMN_METADATA_PATH)

        tables_a_creer = []
        colonnes_a_creer = []

        for table_technique in metadonnees_techniques:
            nom_table = table_technique["nom_table"]
            table_metier = metadonnees_tables.get(nom_table, {})
            colonnes_metier = metadonnees_colonnes.get(nom_table, {})

            table = preparer_table(table_technique, table_metier)
            if table:
                tables_a_creer.append(table)
            colonnes_a_creer.extend(preparer_colonnes(table_technique, colonnes_metier))

        tables_creees = creer_entites(tables_a_creer)
        afficher_creations(tables_a_creer)

        colonnes_creees = creer_entites(colonnes_a_creer)
        afficher_creations(colonnes_a_creer)

        print("Enregistrement Atlas termine")
        print(f"Tables creees: {tables_creees}")
        print(f"Colonnes creees: {colonnes_creees}")
    except (FileNotFoundError, RuntimeError) as erreur:
        print(f"Erreur: {erreur}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
