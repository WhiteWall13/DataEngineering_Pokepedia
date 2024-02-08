# DataEngineering Pokepedia
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Scrapy](https://img.shields.io/badge/Scrapy-%2314D08C.svg?style=for-the-badge&logo=scrapy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![ElasticSearch](https://img.shields.io/badge/Elasticsearch-%23005571.svg?style=for-the-badge&logo=elasticsearch&logoColor=white)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

## Description

Ce projet intègre Docker Compose pour orchestrer une suite de conteneurs, facilitant le scrapage de données, leur stockage et leur visualisation. Utilisant Scrapy pour le scraping de données depuis [Pokepedia](https://www.pokepedia.fr/), les informations collectées sont ensuite traitées et stockées dans une base de données PostgreSQL. ElasticSearch optimise l'accès aux données, tandis que Flask sert à leur affichage interactif sous forme de graphiques et de visualisations web. L'ensemble forme une solution complète pour la manipulation et la présentation de données structurées.


## Prérequis
Pour exécuter ce projet, vous aurez besoin de :
- Docker
- Docker Compose

Assurez-vous que ces outils sont installés et fonctionnels sur votre système.


## Installation et Utilisation
Pour utiliser ce projet, suivez les étapes suivantes :

1. **Construction des images Docker** :
   Placez-vous à la racine du projet et exécutez la commande suivante pour construire les images Docker nécessaires :
```docker-compose build```

2. **Démarrage des conteneurs** :
Une fois les images construites, démarrez les conteneurs avec cette commande : 
```docker-compose up -d```

3. **Accès à la page web**
La page web est accessible à l'adresse suivante :
[http://localhost:8080/](http://localhost:8080/) et 
[http://localhost:8080/pokemons](http://localhost:8080/pokemons)
        
4. **Arrêt des conteneurs et suppression des volumes** :
Pour arrêter les conteneurs et supprimer les volumes associés, utilisez :
```docker-compose down -v```

## Composants
- **Scrapy** : Utilisé pour scraper les données du site [Pokepedia](https://www.pokepedia.fr/). Les spiders de Scrapy récupèrent les données, qui sont ensuite formatées et préparées pour l'insertion dans la base de données PostgreSQL.

- **PostgreSQL** : Base de données relationnelle stockant les données des Pokemons. Chaque Pokémon possède des caractéristiques uniformes, rendant PostgreSQL plus adapté qu'une base de données NoSQL comme MongoDB.

- **ElasticSearch** : Utilisé pour optimiser l'accès aux données. Il facilite la récupération et l'analyse des données pour leur affichage.

- **Flask** : Framework web pour afficher les données sous forme de graphiques et d'autres visualisations. Flask interagit avec ElasticSearch pour récupérer les données à afficher.

## Architecture du Projet
### Conteneurs
Le projet utilise Docker Compose pour orchestrer les conteneurs. Voici les services principaux :

- **scrapy** : Conteneur pour l'exécution de Scrapy et l'insertion des données.
- **db** : Conteneur PostgreSQL pour la base de données.
- **elasticsearch** : Conteneur ElasticSearch pour l'optimisation des données.
- **flask** : Conteneur Flask pour l'affichage web.

Chaque conteneur est configuré dans le fichier `docker-compose.yml`, et les Dockerfiles correspondants sont utilisés pour définir les environnements de chaque service. Cette architecture modulaire permet une gestion efficace et isolée des différents aspects du projet, de la collecte des données à leur présentation.

Voici un schéma de l'architecture du projet :
```mermaid
graph LR
    A[Pokepedia] -->|Scraping via Scrapy| B[JSON]
    B -->|Insertion via insert.py| C[PostgreSQL DB]
    C -->|Alimentation| D[ElasticSearch]
    D -->|Visualisation| E[Flask App sur localhost:8080]

    style A fill:#f00000,stroke:#333,stroke-width:2px
    style B fill:#f00000,stroke:#333,stroke-width:2px
    style C fill:#f00000,stroke:#333,stroke-width:2px
    style D fill:#f00000,stroke:#333,stroke-width:2px
    style E fill:#f00000,stroke:#333,stroke-width:2px
```

### Choix techniques 
#### Utilisation du Fichier JSON
Après le scraping, les données sont enregistrées dans un fichier JSON au sein du conteneur Scrapy avant d'être intégrées à la base de données grâce au fichier `PokepediaScrapy/insert.py`. Ce fichier joue plusieurs rôles clés :
- **Transparence des Données** : Permet une inspection aisée des données scrapées, rendant le processus plus transparent et compréhensible.
- **Facilité de Débogage** : Agit comme un point de vérification pour faciliter le débogage et l'ajustement des données.
- **Flexibilité** : Offre une flexibilité dans le rechargement et le traitement des données.

#### Utilisation de la Base de Données PostgreSQL
La base de données PostgreSQL initialisée par le fichier `Postre_SQL/init.sql` joue un rôle crucial dans le projet :
- **Stockage Structuré** : En tant que base de données relationnelle, PostgreSQL est idéal pour stocker des données structurées, comme les informations détaillées des Pokemons, qui présentent des caractéristiques uniformes et des relations entre elles.
- **Intégrité des Données** : PostgreSQL assure l'intégrité et la cohérence des données, ce qui est essentiel pour maintenir la qualité et la fiabilité des informations stockées.
- **Efficacité des Requêtes** : Grâce à ses capacités avancées de gestion de requêtes, PostgreSQL permet une récupération rapide et efficace des données, ce qui est crucial pour les opérations de recherche et de visualisation de données par les autres composants du projet.

## Author
#### Nicolas Hameau  
- ![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white) [nicolas.hameau@edu.esiee.fr](mailto:nicolas.hameau@edu.esiee.fr)
- ![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white) [Nicolas Hameau](http://linkedin.com/in/nicolas-hameau-13242002)
- ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) [WhiteWall13](https://github.com/WhiteWall13)

#### Bastien Guillou
- ![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white) [bastien.guillou@edu.esiee.fr](mailto:bastien.guillou@edu.esiee.fr)
- ![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white) [Bastien GUILLOU](https://www.linkedin.com/in/bastien-guillou-87021a2b3/)
- ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) [basti2002](https://github.com/basti2002)
