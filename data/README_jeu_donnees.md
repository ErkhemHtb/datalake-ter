# Jeu de données e-commerce / CRM

Ce dossier contient les données utilisées pour la démonstration du TER. On a choisi un petit exemple e-commerce / CRM parce qu'il permet d'avoir plusieurs types de données faciles à expliquer : clients, commandes, paiements, avis et tickets support.

Le but n'est pas de faire une vraie analyse commerciale. Ces fichiers servent surtout à avoir une base simple pour tester le passage de CSV vers Parquet, puis l'ajout de métadonnées et de classifications dans Apache Atlas.

## Fichiers générés

Le script de génération crée les fichiers suivants dans `data/raw/` :

- `clients.csv` : clients fictifs, avec email, téléphone, segment et consentement marketing
- `produits.csv` : catalogue produit simplifié
- `commandes.csv` : commandes liées aux clients
- `paiements.csv` : paiements liés aux commandes, sans vraie donnée bancaire
- `avis_clients.csv` : avis produits avec une note et un commentaire
- `tickets_support.csv` : tickets de support avec un sujet et un message

Ces tables sont volontairement simples. Elles ne représentent pas tout ce qu'on trouverait dans un vrai système e-commerce, mais elles suffisent pour la démonstration.

## Relations entre les tables

Quelques colonnes permettent de relier les fichiers entre eux :

- `commandes.id_client` fait référence à `clients.id_client`
- `paiements.id_commande` fait référence à `commandes.id_commande`
- `avis_clients.id_client` fait référence à `clients.id_client`
- `avis_clients.id_produit` fait référence à `produits.id_produit`
- `tickets_support.id_client` fait référence à `clients.id_client`

Cela permet d'avoir un petit jeu de données cohérent, sans rendre le projet trop lourd.

## Intérêt pour les métadonnées

Ce jeu de données a été construit pour avoir plusieurs cas utiles dans Atlas :

- les colonnes `email` et `telephone` peuvent être vues comme des données personnelles
- la colonne `montant` dans les paiements peut être classée comme donnée financière
- les colonnes `commentaire` et `message` sont des champs texte libre
- les tables ont des domaines différents comme client, vente, finance ou support

Les fichiers du dossier `metadata/` servent ensuite à décrire les tables, les colonnes, les clés et les classifications prévues pour la démonstration.

## Données fictives

Les données sont générées avec Faker. Elles sont donc fictives et ne correspondent pas à de vraies personnes. Une seed fixe est utilisée pour pouvoir recréer le même jeu de données plus facilement.

Le volume reste volontairement petit. L'objectif est de valider le flux de métadonnées et la démonstration dans Atlas, pas de tester des performances ou de faire une analyse e-commerce complète.
