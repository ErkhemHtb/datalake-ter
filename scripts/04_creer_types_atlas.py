from __future__ import annotations

import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from src.client_atlas import requete_get, requete_post, verifier_connexion  # noqa: E402


CLASSIFICATIONS = [
    "DONNEE_PERSONNELLE",
    "DONNEE_SENSIBLE_RGPD",
    "EMAIL",
    "TELEPHONE",
    "DONNEE_FINANCIERE",
    "DONNEE_COMMERCIALE",
    "TEXTE_LIBRE",
    "RISQUE_DONNEE_PERSONNELLE",
    "CLE_PRIMAIRE",
    "CLE_ETRANGERE",
    "NON_SENSIBLE",
]


def attribut(nom: str, type_donnee: str, unique: bool = False, indexable: bool = False) -> dict:
    return {
        "name": nom,
        "typeName": type_donnee,
        "isOptional": True,
        "cardinality": "SINGLE",
        "valuesMinCount": 0,
        "valuesMaxCount": 1,
        "isUnique": unique,
        "isIndexable": indexable,
        "includeInNotification": False,
    }


def type_existe(nom_type: str) -> bool:
    try:
        requete_get(f"types/typedef/name/{nom_type}")
        return True
    except RuntimeError as erreur:
        if "404" in str(erreur) or "Not Found" in str(erreur):
            return False
        raise


def definition_table() -> dict:
    return {
        "category": "ENTITY",
        "name": "datalake_table",
        "description": "Table du data lake utilisee dans le TER",
        "typeVersion": "1.0",
        "serviceType": "datalake",
        "superTypes": [],
        "attributeDefs": [
            attribut("name", "string", indexable=True),
            attribut("qualifiedName", "string", unique=True, indexable=True),
            attribut("description", "string"),
            attribut("domaine", "string", indexable=True),
            attribut("proprietaire", "string", indexable=True),
            attribut("chemin", "string"),
            attribut("format_source", "string"),
            attribut("format_cible", "string"),
            attribut("niveau_sensibilite", "string", indexable=True),
            attribut("statut_qualite", "string"),
            attribut("nombre_lignes", "long"),
            attribut("fichier_source", "string"),
        ],
    }


def definition_colonne() -> dict:
    return {
        "category": "ENTITY",
        "name": "datalake_column",
        "description": "Colonne d'une table du data lake",
        "typeVersion": "1.0",
        "serviceType": "datalake",
        "superTypes": [],
        "attributeDefs": [
            attribut("name", "string", indexable=True),
            attribut("qualifiedName", "string", unique=True, indexable=True),
            attribut("table_name", "string", indexable=True),
            attribut("type_donnee", "string"),
            attribut("description", "string"),
            attribut("est_sensible", "boolean"),
            attribut("concerne_rgpd", "boolean"),
        ],
    }


def definition_classification(nom: str) -> dict:
    return {
        "category": "CLASSIFICATION",
        "name": nom,
        "description": f"Classification {nom} pour le TER data lake",
        "typeVersion": "1.0",
        "superTypes": [],
        "entityTypes": [],
        "attributeDefs": [],
    }


def construire_payload() -> dict:
    entity_defs = []
    classification_defs = []

    for definition in [definition_table(), definition_colonne()]:
        if type_existe(definition["name"]):
            print(f"Type deja present: {definition['name']}")
        else:
            entity_defs.append(definition)

    for nom in CLASSIFICATIONS:
        if type_existe(nom):
            print(f"Classification deja presente: {nom}")
        else:
            classification_defs.append(definition_classification(nom))

    return {
        "enumDefs": [],
        "structDefs": [],
        "classificationDefs": classification_defs,
        "entityDefs": entity_defs,
        "relationshipDefs": [],
    }


def main() -> None:
    try:
        verifier_connexion()
        payload = construire_payload()

        if not payload["entityDefs"] and not payload["classificationDefs"]:
            print("Types Atlas deja a jour")
            return

        requete_post("types/typedefs", payload)

        for definition in payload["entityDefs"]:
            print(f"Type cree: {definition['name']}")
        for definition in payload["classificationDefs"]:
            print(f"Classification creee: {definition['name']}")
    except RuntimeError as erreur:
        print(f"Erreur Atlas: {erreur}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
