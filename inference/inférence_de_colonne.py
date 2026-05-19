from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# BASE DE RÈGLES
# ──────────────────────────────────────────────────────────────────────────────

DATA_TYPE_RULES: dict[str, str] = {
    # Identifiants
    "id_":          "integer",
    "_id":          "integer",
    # Booléens
    "consentement": "boolean",
    "actif":        "boolean",
    "active":       "boolean",
    "is_":          "boolean",
    "has_":         "boolean",
    # Dates
    "date_":        "date",
    "_date":        "date",
    # Montants / prix
    "montant":      "decimal",
    "prix":         "decimal",
    "amount":       "decimal",
    "price":        "decimal",
    "salaire":      "decimal",
    "salary":       "decimal",
    # Entiers
    "stock":        "integer",
    "note":         "integer",
    "quantite":     "integer",
    "quantity":     "integer",
    "count":        "integer",
    # Texte long
    "commentaire":  "string",
    "message":      "string",
    "description":  "string",
    "sujet":        "string",
    # Défaut → string
}

DESCRIPTION_RULES: dict[str, str] = {
    # Clés
    "id_client":        "Identifiant unique du client.",
    "id_produit":       "Identifiant unique du produit.",
    "id_commande":      "Identifiant unique de commande.",
    "id_paiement":      "Identifiant unique du paiement.",
    "id_avis":          "Identifiant unique de l'avis.",
    "id_ticket":        "Identifiant unique du ticket support.",
    # Colonnes communes
    "nom":              "Nom fictif du client.",
    "prenom":           "Prenom fictif du client.",
    "email":            "Adresse email fictive du client.",
    "telephone":        "Numero de telephone fictif du client.",
    "pays":             "Pays declare.",
    "pays_livraison":   "Pays de livraison de la commande.",
    "ville":            "Ville declaree.",
    "date_inscription": "Date d'inscription du client.",
    "date_commande":    "Date de creation de la commande.",
    "date_paiement":    "Date fictive du paiement.",
    "date_avis":        "Date de publication de l'avis.",
    "date_creation":    "Date de creation de l'entite.",
    "date_ajout_catalogue": "Date d'ajout au catalogue.",
    "segment_client":   "Segment marketing du client.",
    "consentement_marketing": "Consentement marketing donne par le client.",
    "nom_produit":      "Nom fictif du produit.",
    "categorie":        "Categorie commerciale du produit.",
    "prix":             "Prix catalogue du produit.",
    "stock":            "Quantite disponible en stock.",
    "fournisseur":      "Fournisseur fictif du produit.",
    "statut":           "Statut de traitement de l'entite.",
    "statut_paiement":  "Statut du paiement.",
    "montant_total":    "Montant total de la commande.",
    "montant":          "Montant paye correspondant au total de commande.",
    "canal_vente":      "Canal par lequel la commande a ete effectuee.",
    "mode_paiement":    "Mode de paiement sans identifiant bancaire.",
    "note":             "Note client comprise entre 1 et 5.",
    "commentaire":      "Commentaire libre fictif du client.",
    "sujet":            "Sujet court du ticket support.",
    "message":          "Message long fictif saisi dans le ticket.",
    "priorite":         "Priorite operationnelle.",
}

# Chaque règle : (keyword_in_column_name, classification_tag)
# Ordre important : du plus spécifique au plus générique.
CLASSIFICATION_RULES: list[tuple[str, str]] = [
    # Clés structurelles
    ("id_client",        "CLE_PRIMAIRE"),
    ("id_produit",       "CLE_PRIMAIRE"),
    ("id_commande",      "CLE_PRIMAIRE"),
    ("id_paiement",      "CLE_PRIMAIRE"),
    ("id_avis",          "CLE_PRIMAIRE"),
    ("id_ticket",        "CLE_PRIMAIRE"),
    # Clés étrangères (id_ dans une table qui n'est pas la table propriétaire)
    # → géré dynamiquement dans _infer_classifications via le paramètre is_fk
    # Données personnelles directes
    ("nom",              "DONNEE_PERSONNELLE"),
    ("prenom",           "DONNEE_PERSONNELLE"),
    ("email",            "DONNEE_PERSONNELLE"),
    ("telephone",        "DONNEE_PERSONNELLE"),
    ("pays",             "DONNEE_PERSONNELLE"),
    ("ville",            "DONNEE_PERSONNELLE"),
    ("consentement",     "DONNEE_PERSONNELLE"),
    ("pays_livraison",   "DONNEE_PERSONNELLE"),
    # Sous-classifications des données personnelles
    ("email",            "EMAIL"),
    ("telephone",        "TELEPHONE"),
    # RGPD — identique aux données personnelles directes
    ("nom",              "DONNEE_SENSIBLE_RGPD"),
    ("prenom",           "DONNEE_SENSIBLE_RGPD"),
    ("email",            "DONNEE_SENSIBLE_RGPD"),
    ("telephone",        "DONNEE_SENSIBLE_RGPD"),
    ("pays",             "DONNEE_SENSIBLE_RGPD"),
    ("ville",            "DONNEE_SENSIBLE_RGPD"),
    ("consentement",     "DONNEE_SENSIBLE_RGPD"),
    ("pays_livraison",   "DONNEE_SENSIBLE_RGPD"),
    # Données financières
    ("montant",          "DONNEE_FINANCIERE"),
    ("prix",             "DONNEE_FINANCIERE"),
    ("mode_paiement",    "DONNEE_FINANCIERE"),
    ("statut_paiement",  "DONNEE_FINANCIERE"),
    ("date_paiement",    "DONNEE_FINANCIERE"),
    # Données commerciales
    ("date_inscription", "DONNEE_COMMERCIALE"),
    ("segment_client",   "DONNEE_COMMERCIALE"),
    ("categorie",        "DONNEE_COMMERCIALE"),
    ("stock",            "DONNEE_COMMERCIALE"),
    ("fournisseur",      "DONNEE_COMMERCIALE"),
    ("date_ajout",       "DONNEE_COMMERCIALE"),
    ("date_commande",    "DONNEE_COMMERCIALE"),
    ("statut",           "DONNEE_COMMERCIALE"),
    ("montant_total",    "DONNEE_COMMERCIALE"),
    ("canal_vente",      "DONNEE_COMMERCIALE"),
    ("note",             "DONNEE_COMMERCIALE"),
    ("date_avis",        "DONNEE_COMMERCIALE"),
    ("nom_produit",      "NON_SENSIBLE"),
    ("priorite",         "NON_SENSIBLE"),
    # Texte libre — risque de contenir des données personnelles non structurées
    ("commentaire",      "TEXTE_LIBRE"),
    ("commentaire",      "RISQUE_DONNEE_PERSONNELLE"),
    ("message",          "TEXTE_LIBRE"),
    ("message",          "RISQUE_DONNEE_PERSONNELLE"),
    ("sujet",            "TEXTE_LIBRE"),
    ("sujet",            "RISQUE_DONNEE_PERSONNELLE"),
]

# Colonnes sensibles → is_sensitive: true
SENSITIVE_KEYWORDS: set[str] = {
    "nom", "prenom", "email", "telephone", "pays", "ville",
    "consentement", "pays_livraison",
    "montant", "montant_total", "prix", "mode_paiement",
    "statut_paiement", "date_paiement",
    "commentaire", "message", "sujet",
    "id_client",  # clé étrangère pointant vers un client
}

# Colonnes RGPD
RGPD_KEYWORDS: set[str] = {
    "nom", "prenom", "email", "telephone", "pays", "ville",
    "consentement", "pays_livraison",
    "commentaire", "message", "sujet",
    "id_client",  # référence à un client = lien indirect vers une personne
}


# ──────────────────────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ──────────────────────────────────────────────────────────────────────────────

def _match_keyword(column_name: str, rules: dict[str, str]) -> str | None:
    """Retourne la première valeur dont la clé est contenue dans column_name."""
    col = column_name.lower()
    for keyword, value in rules.items():
        if keyword in col:
            return value
    return None


def _infer_data_type(column_name: str) -> str:
    result = _match_keyword(column_name, DATA_TYPE_RULES)
    return result or "string"


def _infer_description(column_name: str) -> str:
    col = column_name.lower()
    if col in DESCRIPTION_RULES:
        return DESCRIPTION_RULES[col]
    # Fallback générique
    return f"Colonne '{column_name}'."


def _infer_classifications(column_name: str, is_fk: bool = False) -> list[str]:
    col = column_name.lower()
    tags: list[str] = []

    # Clé primaire ou étrangère en premier
    if col.startswith("id_") and not is_fk:
        tags.append("CLE_PRIMAIRE")
    elif col.startswith("id_") and is_fk:
        tags.append("CLE_ETRANGERE")
        # Une clé étrangère vers clients porte aussi DONNEE_PERSONNELLE
        if "client" in col:
            tags.append("DONNEE_PERSONNELLE")

    # Règles générales (on saute les tags CLE_PRIMAIRE déjà gérés)
    for keyword, tag in CLASSIFICATION_RULES:
        if keyword in col and tag not in tags and not tag.startswith("CLE_"):
            tags.append(tag)

    return tags if tags else ["NON_SENSIBLE"]


def _infer_is_sensitive(column_name: str) -> bool:
    col = column_name.lower()
    return any(kw in col for kw in SENSITIVE_KEYWORDS)


def _infer_rgpd_relevant(column_name: str) -> bool:
    col = column_name.lower()
    return any(kw in col for kw in RGPD_KEYWORDS)


# ──────────────────────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE
# ──────────────────────────────────────────────────────────────────────────────

def infer_column_metadata(column_name: str, is_fk: bool = False) -> dict:

    return {
        "data_type":       _infer_data_type(column_name),
        "description":     _infer_description(column_name),
        "classifications": _infer_classifications(column_name, is_fk=is_fk),
        "is_sensitive":    _infer_is_sensitive(column_name),
        "rgpd_relevant":   _infer_rgpd_relevant(column_name),
    }