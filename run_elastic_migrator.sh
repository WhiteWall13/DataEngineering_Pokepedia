#!/bin/bash

# Attendre que le conteneur scrapy s'arrête
echo "En attente de la fin du conteneur scrapy..."
while [ $(docker ps -f name=scrapy-f status=running -q | wc -l) -gt 0 ]; do
    sleep 1
done

# Attendre 5 secondes supplémentaires
echo "Attente de 5 secondes..."
sleep 5

# Démarrer le conteneur elastic_migrator
echo "Démarrage d'elastic_migrator..."
docker-compose up elastic_migrator
