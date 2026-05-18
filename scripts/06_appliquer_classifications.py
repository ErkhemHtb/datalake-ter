from __future__ import annotations

import sys
from pathlib import Path

import yaml


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from src.client_atlas import requete_get, requete_post, verifier_connexion  # noqa: E402


CLASSIFICATIONS_PATH = BASE_DIR / "metadata" / "classifications_colonnes.yaml"

COLONNES_DEMO = {
    ("clients", "email"): [
        "EMAIL",
        "DONNEE_PERSONNELLE",
        "DONNEE_SENSIBLE_RGPD",
    ],
    ("clients", "telephone"): [
        "TELEPHONE",
        "DONNEE_PERSONNELLE",
        "DONNEE_SENSIBLE_RGPD",
    ],
    ("paiements", "montant"): [
        "DONNEE_FINANCIERE",
    ],
    ("avis_clients", "commentaire"): [
        "TEXTE_LIBRE",
        "RISQUE_DONNEE_PERSONNELLE",
    ],
    ("tickets_support", "message"): [
        "TEXTE_LIBRE",
        "RISQUE_DONNEE_PERSONNELLE",
    ],
}


def lire_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"fichier introuvable: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def qualified_colonne(nom_table: str, nom_colonne: str) -> str:
    return f"datalake://local/{nom_table}/{nom_colonne}@TER"


def trouver_colonne(nom_table: str, nom_colonne: str) -> dict | None:
    try:
        resultat = requete_get(
            "entity/uniqueAttribute/type/datalake_column",
            params={"attr:qualifiedName": qualified_colonne(nom_table, nom_colonne)},
        )
        return resultat.get("entity", {})
    except RuntimeError as erreur:
        if "404" in str(erreur) or "Not Found" in str(erreur):
            print(f"Entite non trouvee: {nom_table}.{nom_colonne}")
            return None
        raise


def classifications_deja_presentes(entite: dict) -> set[str]:
    return {
        classification.get("typeName")
        for classification in entite.get("classifications", []) or []
        if classification.get("typeName")
    }


def appliquer_classification(guid: str, nom_classification: str) -> None:
    requete_post(
        f"entity/guid/{guid}/classifications",
        [{"typeName": nom_classification}],
    )


def classifications_pour_demo(metadonnees: dict, nom_table: str, nom_colonne: str) -> list[str]:
    classifications_yaml = (
        metadonnees.get(nom_table, {})
        .get(nom_colonne, {})
        .get("classifications", [])
    )
    classifications_demo = COLONNES_DEMO[(nom_table, nom_colonne)]
    return [
        nom_classification
        for nom_classification in classifications_demo
        if nom_classification in classifications_yaml
    ]


def traiter_colonne(metadonnees: dict, nom_table: str, nom_colonne: str) -> dict:
    resultat = {"appliquees": 0, "deja_presentes": 0, "non_trouvees": 0, "erreurs": 0}
    entite = trouver_colonne(nom_table, nom_colonne)

    if not entite:
        resultat["non_trouvees"] += 1
        return resultat

    guid = entite["guid"]
    deja_presentes = classifications_deja_presentes(entite)
    classifications = classifications_pour_demo(metadonnees, nom_table, nom_colonne)

    for nom_classification in classifications:
        if nom_classification in deja_presentes:
            resultat["deja_presentes"] += 1
            print(f"Classification deja presente: {nom_table}.{nom_colonne} -> {nom_classification}")
            continue

        try:
            appliquer_classification(guid, nom_classification)
            resultat["appliquees"] += 1
            print(f"Classification appliquee: {nom_table}.{nom_colonne} -> {nom_classification}")
        except RuntimeError as erreur:
            resultat["erreurs"] += 1
            print(f"Erreur classification: {nom_table}.{nom_colonne} -> {nom_classification}: {erreur}")

    return resultat


def additionner(total: dict, resultat: dict) -> None:
    for cle, valeur in resultat.items():
        total[cle] += valeur


def main() -> None:
    total = {"appliquees": 0, "deja_presentes": 0, "non_trouvees": 0, "erreurs": 0}

    try:
        verifier_connexion()
        metadonnees = lire_yaml(CLASSIFICATIONS_PATH)

        for nom_table, nom_colonne in COLONNES_DEMO:
            resultat = traiter_colonne(metadonnees, nom_table, nom_colonne)
            additionner(total, resultat)

        print("Application des classifications terminee")
        print(f"Classifications appliquees: {total['appliquees']}")
        print(f"Classifications deja presentes: {total['deja_presentes']}")
        print(f"Entites non trouvees: {total['non_trouvees']}")
        print(f"Erreurs: {total['erreurs']}")
    except (FileNotFoundError, RuntimeError) as erreur:
        print(f"Erreur: {erreur}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
