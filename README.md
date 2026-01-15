# Real Estate Statistics API

Application Django pour consulter des statistiques sur les charges de copropriété immobilières et importer de nouvelles annonces depuis BienIci.

## Fonctionnalités

*   **Statistiques** : Calcul de la moyenne, du 1er décile (10%) et du 9ème décile (90%) des charges de copropriété.
*   **Filtres** : Filtrage par Ville, Code Postal et Département avec autocomplétion.
*   **Import de données** :
    *   Commande d'import initial via CSV (`dataset_annonces.csv`).
    *   Formulaire d'ajout d'une annonce via son URL `bienici.com` (scraping API).

## Prérequis

*   Python 3.10+
*   pip

## Installation

1.  Cloner le projet

2.  Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

3.  Appliquer les migrations de base de données :
    ```bash
    python3 manage.py migrate
    ```

4.  (Optionnel) Importer le jeu de données initial :
    ```bash
    python3 manage.py import_ads <PATH DU FICHIER DE DONNÉES>
    ```

## Lancement

Démarrer le serveur de développement :

```bash
python3 manage.py runserver
```


## Utilisation

### Consulter les statistiques
Sur la page d'accueil, renseignez une ville ou un département pour voir les statistiques de charges (Moyenne, Q10, Q90).

### Ajouter une annonce
Allez sur `/import/` (bouton "Import Ad").
Ajouter une URL d'une annonce vente de `bienici.com` pour l'ajouter à la base de données.

## Tests

Pour exécuter les tests unitaires et d'intégration :

```bash
python3 manage.py test real_estate_statistics
```
