# Utiliser l'image officielle Python
FROM python:3.10

# Copier le script et les dépendances
COPY ./ElasticSearch/app_elastic.py /app/
COPY ./ElasticSearch/requirements.txt /app/

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances Python
RUN pip install -r requirements.txt

# Commande pour exécuter le script
CMD python app_elastic.py
