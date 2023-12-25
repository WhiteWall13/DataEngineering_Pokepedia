from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://user:password@db:5432/pokepedia_db"
db = SQLAlchemy(app)


class Pokemon(db.Model):
    __tablename__ = "pokemon"
    numero = db.Column(db.String(10), primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    image_mini = db.Column(db.String(255))
    lien = db.Column(db.String(255))
    image = db.Column(db.String(255))


@app.route("/")
def home():
    return (
        "Bienvenue sur mon application Flask! Pour voir les pokemons, allez à /pokemons"
    )


@app.route("/pokemons")
def list_pokemons():
    count = Pokemon.query.count()
    pokemons = Pokemon.query.all()
    pokemons_html = f"<h1>Liste des Pokémons ({count})</h1>"
    pokemons_html += "<ul>"
    for pokemon in pokemons:
        pokemons_html += f"<li>{pokemon.nom}</li>"
    pokemons_html += "</ul>"
    return pokemons_html


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
