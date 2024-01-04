from flask import Flask, render_template_string
from elasticsearch import Elasticsearch
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Connexion à Elasticsearch
es = Elasticsearch(
    ["http://elasticsearch:9200"],  # Utilisez le nom du service Docker pour Elasticsearch
    basic_auth=('elastic', 'password'),
)

@app.route("/")
def home():
    # Page d'accueil de l'appplication web Flask
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
    # Requête ElasticSearch pour compter le nombre total de Pokémon
    count_result = es.count(index="pokemons", body={"query": {"match_all": {}}})
    total_pokemons = count_result['count']

    # Requête ElasticSearch pour récupérer les Pokémons
    search_body = {
        "query": {"match_all": {}},
        "size": 1000
    }
    search_result = es.search(index="pokemons", body=search_body)
    pokemons = search_result['hits']['hits']

    # Génération du HTML pour la liste des Pokémon
    pokemons_html = f"<h1>Liste des Pokémons ({total_pokemons})</h1><ul>"
    for pokemon in pokemons:
        name = pokemon['_source']['nom']
        types = ', '.join(pokemon['_source']['types'])
        pokemons_html += f"<li>{name} - Types: {types}</li>"
    pokemons_html += "</ul>"
    return pokemons_html

@app.route('/statistiques')
def statistiques():
    # Requête ElasticSearch pour les statistiques
    body = {
        "size": 0,
        "aggs": {
            "types_count": {
                "terms": {"field": "types.keyword"} 
            }
        }
    }

    result = es.search(index="pokemons", body=body)
    buckets = result['aggregations']['types_count']['buckets']

    types = [bucket['key'] for bucket in buckets]
    counts = [bucket['doc_count'] for bucket in buckets]

    # Création de l'histogramme avec Plotly
    fig = px.bar(
        x=types,
        y=counts,
        labels={"x": "Type", "y": "Nombre"},
        title="Nombre de Pokémon par Type",
    )

    # Rendu de l'histogramme en HTML
    graph_html = pio.to_html(fig, full_html=False)
    return f"<h1>Voici des statistiques liées aux Pokémon</h1>{graph_html}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
