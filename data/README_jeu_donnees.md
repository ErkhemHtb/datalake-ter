# Dataset synthetique e-commerce / CRM

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
