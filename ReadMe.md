# DataEngineering Pokepedia

## Description
Ce projet utilise Docker Compose pour orchestrer plusieurs conteneurs, notamment pour la base de données PostgreSQL et le scraping avec Python. Le but est de remplir une base de données PostgreSQL avec des données scrapées à l'aide d'un script Python, en utilisant des conteneurs Docker pour gérer les différents services.

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

4. **Accès à la base de donnée**
Si vous souhaitez accèder à la base de donnée :
```docker exec -it postgres_pokepedia psql -U user -d pokepedia_db```
( à supprimer du readme pcq je n'ai pas encore gérer les secrets d'identification)
        
4. **Arrêt des conteneurs et suppression des volumes** :
Pour arrêter les conteneurs et supprimer les volumes associés, utilisez :
```docker-compose down -v```


## Structure du Projet
Le projet est structuré comme suit :
- Un conteneur `db` pour la base de données PostgreSQL.
- Un conteneur `scrapy` pour exécuter le script de scraping et d'insertion de données.
- Un conteneur `flask` pour une application web.

Chaque conteneur est configuré dans le fichier `docker-compose.yml`, et les Dockerfiles correspondants sont utilisés pour définir les environnements de chaque service.


## Licence
TODO

---

Bonne chance avec Flask et Elastic Search (et Kibana?) :wink: