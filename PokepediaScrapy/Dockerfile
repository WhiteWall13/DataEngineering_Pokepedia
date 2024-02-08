FROM python:3.10

# Définit le dossier de travail
WORKDIR /app

# Copie le requirements.txt 
COPY ./PokepediaScrapy/requirements.txt /app/
COPY ./ElasticSearch/requirements.txt /app/ElasticSearch/

# Installaion des dépendances python pour scrapy et la migration des données à elasticsearch
RUN pip install -r /app/requirements.txt
RUN pip install -r /app/ElasticSearch/requirements.txt

# Copier le projet Scrapy 
COPY ./PokepediaScrapy /app/PokepediaScrapy
COPY ./scrapy.cfg /app/

COPY ./ElasticSearch/app_elastic.py /app/ElasticSearch

# Définit le dossier de travail
WORKDIR /app/PokepediaScrapy

# On run le Scrapy et l'insertion des données 
CMD scrapy crawl pokemon && scrapy crawl pokemon_detail && python insert.py && python /app/ElasticSearch/app_elastic.py
