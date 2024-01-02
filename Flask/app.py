from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Configuration de la base de données
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@db:5432/pokepedia_db"
db = SQLAlchemy(app)

# Modèles de base de données
class Type(db.Model):
    __tablename__ = "type"
    type_id = db.Column(db.Integer, primary_key=True)
    type_nom = db.Column(db.String(50), unique=True)

class PokemonType(db.Model):
    __tablename__ = "pokemon_type"
    numero = db.Column(db.String(10), db.ForeignKey('pokemon.numero'), primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type.type_id'), primary_key=True)
    type = db.relationship("Type")

class Pokemon(db.Model):
    __tablename__ = "pokemon"
    numero = db.Column(db.String(10), primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    types = db.relationship('Type', secondary='pokemon_type')

@app.route("/")
def home():
    home_html = """
    <h1>Bienvenue sur mon application Flask!</h1>
    <p>Pour voir les pokemons, cliquez sur le bouton ci-dessous.</p>
    <form action="/pokemons">
        <input type="submit" value="Voir les Pokémons" style="background-color: blue; color: white; font-size: 20px; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-bottom: 10px;" />
    </form>
    <form action="/statistiques">
        <input type="submit" value="Voici les statistiques des pokémons" style="background-color: red; color: white; font-size: 20px; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;" />
    </form>
    """
    return home_html

@app.route("/pokemons")
def list_pokemons():
    pokemons = Pokemon.query.all()
    pokemons_html = "<h1>Liste des Pokémons</h1><ul>"
    for pokemon in pokemons:
        types = ', '.join([t.type_nom for t in pokemon.types])
        pokemons_html += f"<li>{pokemon.nom} - Types: {types}</li>"
    pokemons_html += "</ul>"
    return pokemons_html


@app.route('/statistiques')
def statistiques():
    # Utilisation d'une connexion pour exécuter la requête SQL
    with db.engine.connect() as connection:
        result = connection.execute(text("""
        SELECT type.type_nom, COUNT(pokemon_type.type_id) as count
        FROM type
        JOIN pokemon_type ON type.type_id = pokemon_type.type_id
        GROUP BY type.type_nom
        """))
        
        types = []
        counts = []
        for row in result:
            types.append(row.type_nom)
            counts.append(row.count)

    # Création de l'histogramme avec Plotly
    fig = px.bar(x=types, y=counts, labels={'x': 'Type', 'y': 'Nombre'}, title="Nombre de Pokémon par Type")

    # Rendu de l'histogramme en HTML
    graph_html = pio.to_html(fig, full_html=False)
    return f"<h1>Voici des statistiques liées aux Pokémon</h1>{graph_html}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
