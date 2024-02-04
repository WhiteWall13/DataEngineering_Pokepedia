FROM python:3.10

WORKDIR /app

# Copier et installer les dépendances
COPY ./Flask/requirements.txt /app/
RUN pip install -r requirements.txt

# Copier le code de l'application Flask et les assets statiques
COPY ./Flask /app

EXPOSE 8080

# Variable d'environnement
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Démarre l'application Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
