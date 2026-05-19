from __future__ import annotations

from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# BASE DE RÈGLES
# ──────────────────────────────────────────────────────────────────────────────

DOMAIN_RULES: dict[str, str] = {
    # Support & expérience client (avant "client" générique)
    "avis":        "experience_client",
    "review":      "experience_client",
    "ticket":      "support",
    "support":     "support",
    "incident":    "support",
    # CRM
    "client":      "CRM",
    "customer":    "CRM",
    "user":        "CRM",
    "utilisateur": "CRM",
    # Vente
    "commande":    "vente",
    "order":       "vente",
    "vente":       "vente",
    "sale":        "vente",
    # Catalogue
    "produit":     "catalogue",
    "product":     "catalogue",
    "article":     "catalogue",
    # Finance
    "paiement":    "finance",
    "payment":     "finance",
    "facture":     "finance",
    "invoice":     "finance",
    "budget":      "finance",
    # RH
    "employe":     "RH",
    "employee":    "RH",
    "staff":       "RH",
    "salaire":     "RH",
    "salary":      "RH",
    # Logistique
    "stock":       "logistique",
    "inventory":   "logistique",
    "livraison":   "logistique",
    "shipment":    "logistique",
    # IT
    "log":         "IT",
    "audit":       "IT",
    "session":     "IT",
}

OWNER_BY_DOMAIN: dict[str, str] = {
    "CRM":               "equipe_data",
    "vente":             "equipe_ventes",
    "catalogue":         "equipe_catalogue",
    "finance":           "equipe_finance",
    "experience_client": "equipe_experience_client",
    "support":           "equipe_support",
    "RH":                "equipe_rh",
    "logistique":        "equipe_logistique",
    "IT":                "equipe_it",
}

SENSITIVITY_BY_DOMAIN: dict[str, str] = {
    "CRM":               "high",
    "finance":           "high",
    "RH":                "high",
    "vente":             "medium",
    "support":           "medium",
    "experience_client": "medium",
    "catalogue":         "low",
    "logistique":        "low",
    "IT":                "medium",
}

DESCRIPTION_RULES: dict[str, str] = {
    "avis":     "Avis clients sur des produits du catalogue.",
    "review":   "Avis clients sur des produits du catalogue.",
    "ticket":   "Tickets de support créés par les clients.",
    "support":  "Tickets de support créés par les clients.",
    "client":   "Informations principales des clients inscrits sur la plateforme.",
    "customer": "Informations principales des clients inscrits sur la plateforme.",
    "commande": "Commandes passées par les clients sur les différents canaux de vente.",
    "order":    "Commandes passées par les clients sur les différents canaux de vente.",
    "produit":  "Catalogue des produits vendus par la plateforme.",
    "product":  "Catalogue des produits vendus par la plateforme.",
    "paiement": "Paiements associés aux commandes.",
    "payment":  "Paiements associés aux commandes.",
    "facture":  "Factures émises aux clients.",
    "invoice":  "Factures émises aux clients.",
    "employe":  "Données des employés de l'organisation.",
    "employee": "Données des employés de l'organisation.",
    "stock":    "Niveaux de stock des produits en entrepôt.",
    "log":      "Journaux techniques d'événements système.",
    "audit":    "Traces d'audit pour la traçabilité des actions.",
}

BUSINESS_USE_BY_DOMAIN: dict[str, str] = {
    "CRM":               "Analyse client, segmentation, conformite RGPD et gouvernance du consentement.",
    "vente":             "Analyse des ventes, parcours client, relations metier et lignage entre CRM et ventes.",
    "catalogue":         "Analyse de catalogue, suivi des prix, stock et fournisseurs.",
    "finance":           "Suivi financier, rapprochement commande-paiement et classification des donnees financieres.",
    "experience_client": "Analyse de satisfaction, recherche textuelle et demonstration du risque sur champs libres.",
    "support":           "Analyse des incidents, priorisation support et gouvernance des messages en texte libre.",
    "RH":                "Gestion des employes, contrats, remunerations et conformite sociale.",
    "logistique":        "Suivi des stocks, entrepots et expeditions.",
    "IT":                "Journalisation technique, gestion des acces et audit systeme.",
}

# Cas particuliers pour la clé primaire (singulier irrégulier)
PRIMARY_KEY_OVERRIDES: dict[str, str] = {
    "avis_clients":    "id_avis",
    "tickets_support": "id_ticket",
    "avis":            "id_avis",
    "paiements":       "id_paiement",
    "commandes":       "id_commande",
    "produits":        "id_produit",
    "clients":         "id_client",
}


# ──────────────────────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ──────────────────────────────────────────────────────────────────────────────

def _match_keyword(name: str, rules: dict[str, str]) -> str | None:
    """Retourne la première valeur dont la clé est contenue dans name."""
    name_lower = name.lower()
    for keyword, value in rules.items():
        if keyword in name_lower:
            return value
    return None


def _infer_primary_key(table_name: str) -> str:
    """Génère la clé primaire : vérifie les overrides, sinon id_<singulier>."""
    if table_name in PRIMARY_KEY_OVERRIDES:
        return PRIMARY_KEY_OVERRIDES[table_name]
    singular = table_name.lower().rstrip("s")
    return f"id_{singular}"


# ──────────────────────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE
# ──────────────────────────────────────────────────────────────────────────────

def infer_table_metadata(
    table_name: str,
    expected_number_of_rows: int | None = None,
    source_format: str = "csv",
    target_format: str = "parquet",
    quality_status: str = "basic_checks_passed",
    foreign_keys: list[dict[str, str]] | None = None,
) -> dict[str, Any]:

    domain      = _match_keyword(table_name, DOMAIN_RULES)      or "inconnu"
    description = _match_keyword(table_name, DESCRIPTION_RULES) or f"Table '{table_name}'."

    return {
        "name":                    table_name,
        "description":             description,
        "domain":                  domain,
        "owner":                   OWNER_BY_DOMAIN.get(domain,      "equipe_data"),
        "source_format":           source_format,
        "target_format":           target_format,
        "sensitivity_level":       SENSITIVITY_BY_DOMAIN.get(domain, "medium"),
        "quality_status":          quality_status,
        "expected_number_of_rows": expected_number_of_rows,
        "primary_key":             _infer_primary_key(table_name),
        "foreign_keys":            foreign_keys or [],
        "business_use":            BUSINESS_USE_BY_DOMAIN.get(domain, "Usage interne — finalite a preciser."),
    }