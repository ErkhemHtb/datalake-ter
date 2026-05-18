# TER Master 1 DataScale - métadonnées dans un lac de données

Ce dépôt contient notre travail de TER sur la gestion des métadonnées dans un lac de données.

L'idée est de simuler un petit lac de données avec des fichiers e-commerce, puis de montrer comment on peut décrire les tables, les colonnes et certaines données sensibles avec Apache Atlas.

Le jeu de données est synthétique. Il contient des clients, des produits, des commandes, des paiements, des avis clients et des tickets support. Ce n'est pas un vrai système e-commerce complet, mais cela suffit pour avoir plusieurs cas intéressants : données personnelles, données financières et champs texte libre.

## Idée du projet

Le projet suit ce chemin :

```text
CSV -> Parquet -> métadonnées -> Apache Atlas -> classifications -> recherche dans Atlas UI
```

On commence avec des fichiers CSV dans une zone brute, puis on les convertit en Parquet. Ensuite, un script extrait des métadonnées techniques comme les colonnes, les types, le nombre de lignes et la taille des fichiers.

À côté de ça, des fichiers YAML ajoutent des informations plus métier : description des tables, domaine, sensibilité, qualité, classifications prévues, etc.

Enfin, les tables et colonnes sont envoyées dans Apache Atlas. Atlas sert ensuite à visualiser les métadonnées et à rechercher les colonnes annotées.

## Contenu du dépôt

Les scripts principaux sont dans le dossier `scripts/` :

- `01_generer_jeu_donnees.py` : génère les fichiers CSV et les fichiers YAML
- `02_convertir_en_parquet.py` : convertit les CSV en fichiers Parquet
- `03_extraire_metadonnees.py` : extrait les métadonnées techniques des fichiers Parquet
- `verifier_connexion_atlas.py` : vérifie que l'API Atlas répond
- `04_creer_types_atlas.py` : crée les types et classifications dans Atlas
- `05_enregistrer_entites_atlas.py` : enregistre les tables et colonnes dans Atlas
- `06_appliquer_classifications.py` : applique quelques classifications utiles pour la démo

Les données sont rangées dans `data/` :

- `data/raw/` : fichiers CSV générés localement
- `data/structured/` : fichiers Parquet générés localement
- `data/iceberg/` : dossier gardé seulement pour une perspective Iceberg

Les métadonnées sont dans `metadata/` :

- `metadonnees_tables.yaml` : description métier des tables
- `classifications_colonnes.yaml` : classifications prévues pour les colonnes
- `metadonnees_extraites.json` : métadonnées techniques extraites automatiquement

Le dossier `src/` contient le petit client Python utilisé pour communiquer avec Atlas.

Le dossier `tests/` contient des tests simples pour vérifier que les fichiers générés restent cohérents.

Le dossier `docs/` sert seulement à nos notes de préparation locales. Il n'est pas inclus sur GitHub.

## Lancer le projet

Depuis la racine du projet, installer d'abord les dépendances :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ensuite, lancer les scripts dans cet ordre :

```powershell
python scripts\01_generer_jeu_donnees.py
python scripts\02_convertir_en_parquet.py
python scripts\03_extraire_metadonnees.py
```

Puis lancer Apache Atlas :

```powershell
docker compose up -d
python scripts\verifier_connexion_atlas.py
```

Quand Atlas répond, lancer les scripts liés au catalogue :

```powershell
python scripts\04_creer_types_atlas.py
python scripts\05_enregistrer_entites_atlas.py
python scripts\06_appliquer_classifications.py
```

Les CSV sont générés dans `data/raw/`, les fichiers Parquet dans `data/structured/`, et les métadonnées extraites dans `metadata/metadonnees_extraites.json`.

## Vérifier les tests

Pour lancer les tests :

```powershell
python -B -m unittest discover -s tests
```

Le résultat attendu est :

```text
OK
```

## Utilisation d'Apache Atlas

Apache Atlas est utilisé ici comme catalogue de métadonnées.

Dans notre cas, il permet de voir :

- les tables du lac de données
- les colonnes importantes
- les classifications appliquées
- les données personnelles ou financières
- les champs texte libre à surveiller

L'interface est accessible ici :

```text
http://localhost:21000
```

Identifiants utilisés en local :

```text
admin / admin
```

Pendant la démo, la recherche se fait directement dans l'interface web d'Atlas. On peut par exemple chercher :

- `DONNEE_PERSONNELLE`
- `DONNEE_SENSIBLE_RGPD`
- `EMAIL`
- `TELEPHONE`
- `DONNEE_FINANCIERE`
- `TEXTE_LIBRE`

Exemples de colonnes à montrer :

- `clients.email`
- `clients.telephone`
- `paiements.montant`
- `avis_clients.commentaire`
- `tickets_support.message`

## Pourquoi la recherche est faite dans l'interface Atlas

Au départ, on pouvait envisager une recherche automatisée avec l'API Atlas. Finalement, on a gardé une recherche manuelle dans l'interface, car c'est plus simple pour la soutenance et plus stable avec notre installation locale.

Cela reste cohérent avec le rôle d'Atlas : c'est un catalogue que l'on peut consulter pour retrouver des données et leurs métadonnées.

## Place d'Iceberg

Apache Iceberg n'est pas utilisé dans le code actuel.

On utilise surtout CSV et Parquet pour garder une preuve de concept simple. Iceberg reste une piste d'amélioration, car il permettrait de gérer plus proprement les tables d'un data lake avec des snapshots, un historique et une évolution de schéma.

## Limites

Le projet reste une preuve de concept.

Les données sont synthétiques, les volumes sont petits et les classifications sont appliquées seulement sur quelques colonnes représentatives. C'est volontaire : le but est surtout de montrer le principe de gestion des métadonnées, pas de construire une plateforme complète.

Atlas peut aussi être lent au démarrage. Il vaut mieux le lancer quelques minutes avant la démonstration.

## Usage de l'IA

Des outils d'IA générative ont été utilisés comme aide pour structurer certaines parties du travail, relire des explications et améliorer la rédaction. Le code, les tests, l'adaptation du projet et la validation de la démo ont ensuite été vérifiés par l'équipe.
