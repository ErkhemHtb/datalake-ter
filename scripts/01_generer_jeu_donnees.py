from __future__ import annotations

import random
from datetime import date
from pathlib import Path

import pandas as pd
import yaml
from faker import Faker


SEED = 42
REFERENCE_DATE = date(2026, 5, 16)

N_CLIENTS = 1_000
N_PRODUCTS = 200
N_ORDERS = 3_000
N_REVIEWS = 1_200
N_SUPPORT_TICKETS = 500

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
DATA_DIR = BASE_DIR / "data"
METADATA_DIR = BASE_DIR / "metadata"

# dates fixes pour garder le dataset reproductible
CLIENT_START_DATE = date(2021, 5, 16)
CLIENT_END_DATE = date(2026, 4, 16)
PRODUCT_START_DATE = date(2022, 5, 16)
PRODUCT_END_DATE = date(2026, 5, 9)
ORDER_START_DATE = date(2023, 5, 16)
SUPPORT_START_DATE = date(2024, 5, 16)

CLIENT_SEGMENTS = ["standard", "premium", "vip"]
PRODUCT_CATEGORIES = ["beaute", "high-tech", "mode", "maison", "sport", "livre"]
ORDER_STATUSES = ["en_attente", "payee", "expediee", "livree", "annulee"]
SALES_CHANNELS = ["site_web", "mobile", "marketplace"]
PAYMENT_MODES = ["CB", "PayPal", "Virement", "Apple Pay"]
SUPPORT_PRIORITIES = ["basse", "moyenne", "haute", "critique"]
SUPPORT_STATUSES = ["ouvert", "en_cours", "resolu", "ferme"]

fake = Faker("fr_FR")
Faker.seed(SEED)
random.seed(SEED)


def ensure_directories() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def random_date(start: date, end: date) -> str:
    return fake.date_between(start_date=start, end_date=end).isoformat()


def rounded_amount(value: float) -> float:
    return round(value, 2)


def generate_clients() -> pd.DataFrame:
    rows = []
    for id_client in range(1, N_CLIENTS + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        rows.append(
            {
                "id_client": id_client,
                "nom": last_name,
                "prenom": first_name,
                "email": fake.safe_email(),
                "telephone": fake.phone_number(),
                "pays": fake.country(),
                "ville": fake.city(),
                "date_inscription": random_date(CLIENT_START_DATE, CLIENT_END_DATE),
                "segment_client": random.choices(CLIENT_SEGMENTS, weights=[0.72, 0.23, 0.05], k=1)[0],
                "consentement_marketing": random.choice([True, False]),
            }
        )
    return pd.DataFrame(rows)


def generate_products() -> pd.DataFrame:
    rows = []
    for id_produit in range(1, N_PRODUCTS + 1):
        categorie = random.choice(PRODUCT_CATEGORIES)
        rows.append(
            {
                "id_produit": id_produit,
                "nom_produit": f"{fake.word().capitalize()} {categorie} {id_produit:03d}",
                "categorie": categorie,
                "prix": rounded_amount(random.uniform(5.0, 1_500.0)),
                "stock": random.randint(0, 500),
                "fournisseur": fake.company(),
                "date_ajout_catalogue": random_date(PRODUCT_START_DATE, PRODUCT_END_DATE),
            }
        )
    return pd.DataFrame(rows)


def generate_orders(clients: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    client_ids = clients["id_client"].tolist()
    product_prices = products["prix"].tolist()
    rows = []

    for id_commande in range(1, N_ORDERS + 1):
        item_count = random.randint(1, 5)
        selected_prices = random.choices(product_prices, k=item_count)
        amount = sum(price * random.randint(1, 3) for price in selected_prices)

        rows.append(
            {
                "id_commande": id_commande,
                "id_client": random.choice(client_ids),
                "date_commande": random_date(ORDER_START_DATE, REFERENCE_DATE),
                "statut": random.choices(ORDER_STATUSES, weights=[0.08, 0.18, 0.22, 0.44, 0.08], k=1)[0],
                "montant_total": rounded_amount(amount),
                "canal_vente": random.choices(SALES_CHANNELS, weights=[0.56, 0.31, 0.13], k=1)[0],
                "pays_livraison": fake.country(),
            }
        )
    return pd.DataFrame(rows)


def generate_payments(orders: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for id_paiement, order in enumerate(orders.itertuples(index=False), start=1):
        if order.statut == "annulee":
            payment_status = random.choices(["refuse", "rembourse", "en_attente"], weights=[0.45, 0.35, 0.20], k=1)[0]
        elif order.statut == "en_attente":
            payment_status = random.choices(["en_attente", "refuse"], weights=[0.80, 0.20], k=1)[0]
        else:
            payment_status = random.choices(["accepte", "rembourse"], weights=[0.95, 0.05], k=1)[0]

        rows.append(
            {
                "id_paiement": id_paiement,
                "id_commande": order.id_commande,
                "mode_paiement": random.choice(PAYMENT_MODES),
                "montant": order.montant_total,
                "statut_paiement": payment_status,
                "date_paiement": order.date_commande,
            }
        )
    return pd.DataFrame(rows)


def generate_reviews(clients: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    client_ids = clients["id_client"].tolist()
    product_ids = products["id_produit"].tolist()
    rows = []

    for id_avis in range(1, N_REVIEWS + 1):
        rows.append(
            {
                "id_avis": id_avis,
                "id_client": random.choice(client_ids),
                "id_produit": random.choice(product_ids),
                "note": random.randint(1, 5),
                "commentaire": fake.sentence(nb_words=random.randint(8, 18)),
                "date_avis": random_date(ORDER_START_DATE, REFERENCE_DATE),
            }
        )
    return pd.DataFrame(rows)


def generate_support_tickets(clients: pd.DataFrame) -> pd.DataFrame:
    client_ids = clients["id_client"].tolist()
    subjects = [
        "Question sur une commande",
        "Probleme de livraison",
        "Demande de remboursement",
        "Changement d'adresse",
        "Information produit",
        "Compte client",
    ]
    rows = []

    for id_ticket in range(1, N_SUPPORT_TICKETS + 1):
        rows.append(
            {
                "id_ticket": id_ticket,
                "id_client": random.choice(client_ids),
                "sujet": random.choice(subjects),
                "message": fake.paragraph(nb_sentences=random.randint(2, 5)),
                "priorite": random.choices(SUPPORT_PRIORITIES, weights=[0.34, 0.42, 0.18, 0.06], k=1)[0],
                "statut": random.choices(SUPPORT_STATUSES, weights=[0.18, 0.24, 0.38, 0.20], k=1)[0],
                "date_creation": random_date(SUPPORT_START_DATE, REFERENCE_DATE),
            }
        )
    return pd.DataFrame(rows)


def build_table_metadata() -> dict:
    return {
        "clients": {
            "name": "clients",
            "description": "Informations principales des clients inscrits sur la plateforme e-commerce.",
            "domain": "CRM",
            "owner": "equipe_data",
            "source_format": "csv",
            "target_format": "parquet",
            "sensitivity_level": "high",
            "quality_status": "basic_checks_passed",
            "expected_number_of_rows": N_CLIENTS,
            "primary_key": "id_client",
            "foreign_keys": [],
            "business_use": "Analyse client, segmentation, conformite RGPD et gouvernance du consentement.",
        },
        "produits": {
            "name": "produits",
            "description": "Catalogue fictif des produits vendus par la plateforme.",
            "domain": "catalogue",
            "owner": "equipe_catalogue",
            "source_format": "csv",
            "target_format": "parquet",
            "sensitivity_level": "low",
            "quality_status": "basic_checks_passed",
            "expected_number_of_rows": N_PRODUCTS,
            "primary_key": "id_produit",
            "foreign_keys": [],
            "business_use": "Analyse de catalogue, suivi des prix, stock et fournisseurs.",
        },
        "commandes": {
            "name": "commandes",
            "description": "Commandes passees par les clients sur les differents canaux de vente.",
            "domain": "vente",
            "owner": "equipe_data",
            "source_format": "csv",
            "target_format": "parquet",
            "sensitivity_level": "medium",
            "quality_status": "basic_checks_passed",
            "expected_number_of_rows": N_ORDERS,
            "primary_key": "id_commande",
            "foreign_keys": [{"column": "id_client", "references": "clients.id_client"}],
            "business_use": "Analyse des ventes, parcours client, relations metier et lignage entre CRM et ventes.",
        },
        "paiements": {
            "name": "paiements",
            "description": "Paiements fictifs associes aux commandes, sans donnees bancaires exploitables.",
            "domain": "finance",
            "owner": "equipe_finance",
            "source_format": "csv",
            "target_format": "parquet",
            "sensitivity_level": "high",
            "quality_status": "basic_checks_passed",
            "expected_number_of_rows": N_ORDERS,
            "primary_key": "id_paiement",
            "foreign_keys": [{"column": "id_commande", "references": "commandes.id_commande"}],
            "business_use": "Suivi financier, rapprochement commande-paiement et classification des donnees financieres.",
        },
        "avis_clients": {
            "name": "avis_clients",
            "description": "Avis fictifs de clients sur des produits du catalogue.",
            "domain": "experience_client",
            "owner": "equipe_experience_client",
            "source_format": "csv",
            "target_format": "parquet",
            "sensitivity_level": "medium",
            "quality_status": "basic_checks_passed",
            "expected_number_of_rows": N_REVIEWS,
            "primary_key": "id_avis",
            "foreign_keys": [
                {"column": "id_client", "references": "clients.id_client"},
                {"column": "id_produit", "references": "produits.id_produit"},
            ],
            "business_use": "Analyse de satisfaction, recherche textuelle et demonstration du risque sur champs libres.",
        },
        "tickets_support": {
            "name": "tickets_support",
            "description": "Tickets de support fictifs crees par les clients.",
            "domain": "support",
            "owner": "equipe_support",
            "source_format": "csv",
            "target_format": "parquet",
            "sensitivity_level": "medium",
            "quality_status": "basic_checks_passed",
            "expected_number_of_rows": N_SUPPORT_TICKETS,
            "primary_key": "id_ticket",
            "foreign_keys": [{"column": "id_client", "references": "clients.id_client"}],
            "business_use": "Analyse des incidents, priorisation support et gouvernance des messages en texte libre.",
        },
    }


def column_meta(data_type: str, description: str, classifications: list[str], is_sensitive: bool, rgpd_relevant: bool) -> dict:
    return {
        "data_type": data_type,
        "description": description,
        "classifications": classifications,
        "is_sensitive": is_sensitive,
        "rgpd_relevant": rgpd_relevant,
    }


def build_column_classifications() -> dict:
    return {
        "clients": {
            "id_client": column_meta("integer", "Identifiant unique du client.", ["CLE_PRIMAIRE"], False, False),
            "nom": column_meta("string", "Nom fictif du client.", ["DONNEE_PERSONNELLE", "DONNEE_SENSIBLE_RGPD"], True, True),
            "prenom": column_meta("string", "Prenom fictif du client.", ["DONNEE_PERSONNELLE", "DONNEE_SENSIBLE_RGPD"], True, True),
            "email": column_meta("string", "Adresse email fictive du client.", ["DONNEE_PERSONNELLE", "EMAIL", "DONNEE_SENSIBLE_RGPD"], True, True),
            "telephone": column_meta("string", "Numero de telephone fictif du client.", ["DONNEE_PERSONNELLE", "TELEPHONE", "DONNEE_SENSIBLE_RGPD"], True, True),
            "pays": column_meta("string", "Pays declare pour le client.", ["DONNEE_PERSONNELLE"], True, True),
            "ville": column_meta("string", "Ville declaree pour le client.", ["DONNEE_PERSONNELLE"], True, True),
            "date_inscription": column_meta("date", "Date d'inscription du client.", ["DONNEE_COMMERCIALE"], False, False),
            "segment_client": column_meta("string", "Segment marketing du client.", ["DONNEE_COMMERCIALE"], False, False),
            "consentement_marketing": column_meta("boolean", "Consentement marketing donne par le client.", ["DONNEE_PERSONNELLE"], True, True),
        },
        "produits": {
            "id_produit": column_meta("integer", "Identifiant unique du produit.", ["CLE_PRIMAIRE"], False, False),
            "nom_produit": column_meta("string", "Nom fictif du produit.", ["NON_SENSIBLE"], False, False),
            "categorie": column_meta("string", "Categorie commerciale du produit.", ["DONNEE_COMMERCIALE"], False, False),
            "prix": column_meta("decimal", "Prix catalogue du produit.", ["DONNEE_COMMERCIALE"], False, False),
            "stock": column_meta("integer", "Quantite disponible en stock.", ["DONNEE_COMMERCIALE"], False, False),
            "fournisseur": column_meta("string", "Fournisseur fictif du produit.", ["DONNEE_COMMERCIALE"], False, False),
            "date_ajout_catalogue": column_meta("date", "Date d'ajout au catalogue.", ["DONNEE_COMMERCIALE"], False, False),
        },
        "commandes": {
            "id_commande": column_meta("integer", "Identifiant unique de commande.", ["CLE_PRIMAIRE"], False, False),
            "id_client": column_meta("integer", "Reference vers le client ayant passe la commande.", ["CLE_ETRANGERE", "DONNEE_PERSONNELLE"], True, True),
            "date_commande": column_meta("date", "Date de creation de la commande.", ["DONNEE_COMMERCIALE"], False, False),
            "statut": column_meta("string", "Statut metier de la commande.", ["DONNEE_COMMERCIALE"], False, False),
            "montant_total": column_meta("decimal", "Montant total de la commande.", ["DONNEE_FINANCIERE", "DONNEE_COMMERCIALE"], True, False),
            "canal_vente": column_meta("string", "Canal par lequel la commande a ete effectuee.", ["DONNEE_COMMERCIALE"], False, False),
            "pays_livraison": column_meta("string", "Pays de livraison de la commande.", ["DONNEE_PERSONNELLE"], True, True),
        },
        "paiements": {
            "id_paiement": column_meta("integer", "Identifiant unique du paiement.", ["CLE_PRIMAIRE"], False, False),
            "id_commande": column_meta("integer", "Reference vers la commande payee.", ["CLE_ETRANGERE"], False, False),
            "mode_paiement": column_meta("string", "Mode de paiement sans identifiant bancaire.", ["DONNEE_FINANCIERE"], True, False),
            "montant": column_meta("decimal", "Montant paye correspondant au total de commande.", ["DONNEE_FINANCIERE"], True, False),
            "statut_paiement": column_meta("string", "Statut du paiement.", ["DONNEE_FINANCIERE"], True, False),
            "date_paiement": column_meta("date", "Date fictive du paiement.", ["DONNEE_FINANCIERE"], True, False),
        },
        "avis_clients": {
            "id_avis": column_meta("integer", "Identifiant unique de l'avis.", ["CLE_PRIMAIRE"], False, False),
            "id_client": column_meta("integer", "Reference vers le client auteur de l'avis.", ["CLE_ETRANGERE", "DONNEE_PERSONNELLE"], True, True),
            "id_produit": column_meta("integer", "Reference vers le produit evalue.", ["CLE_ETRANGERE"], False, False),
            "note": column_meta("integer", "Note client comprise entre 1 et 5.", ["DONNEE_COMMERCIALE"], False, False),
            "commentaire": column_meta("string", "Commentaire libre fictif du client.", ["TEXTE_LIBRE", "RISQUE_DONNEE_PERSONNELLE"], True, True),
            "date_avis": column_meta("date", "Date de publication de l'avis.", ["DONNEE_COMMERCIALE"], False, False),
        },
        "tickets_support": {
            "id_ticket": column_meta("integer", "Identifiant unique du ticket support.", ["CLE_PRIMAIRE"], False, False),
            "id_client": column_meta("integer", "Reference vers le client ayant ouvert le ticket.", ["CLE_ETRANGERE", "DONNEE_PERSONNELLE"], True, True),
            "sujet": column_meta("string", "Sujet court du ticket support.", ["TEXTE_LIBRE", "RISQUE_DONNEE_PERSONNELLE"], True, True),
            "message": column_meta("string", "Message long fictif saisi dans le ticket.", ["TEXTE_LIBRE", "RISQUE_DONNEE_PERSONNELLE"], True, True),
            "priorite": column_meta("string", "Priorite operationnelle du ticket.", ["NON_SENSIBLE"], False, False),
            "statut": column_meta("string", "Statut de traitement du ticket.", ["NON_SENSIBLE"], False, False),
            "date_creation": column_meta("date", "Date de creation du ticket.", ["NON_SENSIBLE"], False, False),
        },
    }


def write_metadata_files() -> None:
    table_metadata_path = METADATA_DIR / "metadonnees_tables.yaml"
    column_classifications_path = METADATA_DIR / "classifications_colonnes.yaml"

    with table_metadata_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(build_table_metadata(), file, sort_keys=False, allow_unicode=True)

    with column_classifications_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(build_column_classifications(), file, sort_keys=False, allow_unicode=True)


def validate_relationships(
    clients: pd.DataFrame,
    products: pd.DataFrame,
    orders: pd.DataFrame,
    payments: pd.DataFrame,
    reviews: pd.DataFrame,
    support_tickets: pd.DataFrame,
) -> None:
    client_ids = set(clients["id_client"])
    product_ids = set(products["id_produit"])
    order_ids = set(orders["id_commande"])

    checks = {
        "commandes.id_client": set(orders["id_client"]).issubset(client_ids),
        "paiements.id_commande": set(payments["id_commande"]).issubset(order_ids),
        "avis_clients.id_client": set(reviews["id_client"]).issubset(client_ids),
        "avis_clients.id_produit": set(reviews["id_produit"]).issubset(product_ids),
        "tickets_support.id_client": set(support_tickets["id_client"]).issubset(client_ids),
    }
    failed = [name for name, is_valid in checks.items() if not is_valid]
    if failed:
        raise ValueError(f"Cles etrangeres invalides: {', '.join(failed)}")

    merged = payments.merge(orders[["id_commande", "montant_total"]], on="id_commande", how="left")
    if not (merged["montant"] == merged["montant_total"]).all():
        raise ValueError("Les montants de paiement ne correspondent pas aux montants des commandes.")


def write_readme() -> None:
    readme = """# Dataset synthetique e-commerce / CRM

Ce dataset sert de base pour notre preuve de concept sur les metadonnees dans un lac de donnees. Il ne cherche pas a reproduire tout le fonctionnement d'un vrai SI e-commerce, mais il donne assez de tables et de relations pour tester les annotations dans un catalogue.

## Tables

- `clients.csv` : clients fictifs, segment et consentement marketing
- `produits.csv` : catalogue produit simplifie
- `commandes.csv` : commandes rattachees aux clients
- `paiements.csv` : paiements rattaches aux commandes, sans donnees bancaires reelles
- `avis_clients.csv` : avis produits avec un commentaire libre
- `tickets_support.csv` : tickets de support avec sujet et message

## Relations

- `commandes.id_client` reference `clients.id_client`
- `paiements.id_commande` reference `commandes.id_commande`
- `avis_clients.id_client` reference `clients.id_client`
- `avis_clients.id_produit` reference `produits.id_produit`
- `tickets_support.id_client` reference `clients.id_client`

## Interet pour les metadonnees

Les fichiers YAML du dossier `metadata/` decrivent les tables, les colonnes, les cles et quelques classifications. Ils serviront ensuite a alimenter Apache Atlas dans la suite du projet.

Exemples utiles pour la demo :

- retrouver les colonnes contenant des donnees personnelles
- distinguer les donnees financieres des donnees catalogue
- montrer que les champs libres sont plus difficiles a gouverner

## Donnees synthetiques

Les donnees sont generees avec Faker, une seed fixe et des bornes de dates fixes. Les emails utilisent `safe_email()`. Les noms, villes, entreprises et messages sont fictifs.

Limite importante : ce dataset reste volontairement simple. Il sert surtout a tester le flux de metadonnees, pas a faire une analyse e-commerce complete.
"""
    (DATA_DIR / "README_jeu_donnees.md").write_text(readme, encoding="utf-8")


def write_csv_files(datasets: dict[str, pd.DataFrame]) -> None:
    for table_name, dataframe in datasets.items():
        dataframe.to_csv(RAW_DIR / f"{table_name}.csv", index=False, encoding="utf-8")


def print_summary(datasets: dict[str, pd.DataFrame]) -> None:
    print("Dataset genere")
    print("\nCSV crees:")
    for table_name, dataframe in datasets.items():
        print(f"- {table_name}: {len(dataframe)} lignes -> {RAW_DIR / f'{table_name}.csv'}")

    print("\nMetadonnees creees:")
    print(f"- {METADATA_DIR / 'metadonnees_tables.yaml'}")
    print(f"- {METADATA_DIR / 'classifications_colonnes.yaml'}")
    print(f"- {DATA_DIR / 'README_jeu_donnees.md'}")


def main() -> None:
    ensure_directories()

    clients = generate_clients()
    products = generate_products()
    orders = generate_orders(clients, products)
    payments = generate_payments(orders)
    reviews = generate_reviews(clients, products)
    support_tickets = generate_support_tickets(clients)

    validate_relationships(clients, products, orders, payments, reviews, support_tickets)

    datasets = {
        "clients": clients,
        "produits": products,
        "commandes": orders,
        "paiements": payments,
        "avis_clients": reviews,
        "tickets_support": support_tickets,
    }
    write_csv_files(datasets)
    write_metadata_files()
    write_readme()
    print_summary(datasets)


if __name__ == "__main__":
    main()
