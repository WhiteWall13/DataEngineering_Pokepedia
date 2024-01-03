FROM python:3.10

# Set working directory
WORKDIR /app

# Install requirements
COPY ./PokepediaScrapy/requirements.txt /app/
RUN pip install -r /app/requirements.txt

# Copy Scrapy project
COPY ./PokepediaScrapy /app/PokepediaScrapy
COPY ./scrapy.cfg /app/

# Change working directory
WORKDIR /app/PokepediaScrapy

# Run Scrapy and insertion script
CMD scrapy crawl pokemon && scrapy crawl pokemon_detail && python insert.py; sleep 600
