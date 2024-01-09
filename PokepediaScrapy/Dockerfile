FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements.txt files to directory
COPY ./PokepediaScrapy/requirements.txt /app/
COPY ./ElasticSearch/requirements.txt /app/ElasticSearch/

# Install Python dependencies for scrapy and data migration to elasticsearch
RUN pip install -r /app/requirements.txt
RUN pip install -r /app/ElasticSearch/requirements.txt

# Copy Scrapy project
COPY ./PokepediaScrapy /app/PokepediaScrapy
COPY ./scrapy.cfg /app/

COPY ./ElasticSearch/app_elastic.py /app/ElasticSearch

# Change working directory
WORKDIR /app/PokepediaScrapy

# Run Scrapy and insertion script
CMD scrapy crawl pokemon && scrapy crawl pokemon_detail && python insert.py && python /app/ElasticSearch/app_elastic.py
