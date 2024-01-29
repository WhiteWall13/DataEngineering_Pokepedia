from flask import Flask, render_template_string
from elasticsearch import Elasticsearch
import plotly.express as px
import plotly.io as pio
from statistics import mean
from flask import request

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
    <form action="/pokemons_sensibilities">
        <input type="submit" value="Voir les Pokémons et leurs sensibilités" style="background-color: green; color: white; font-size: 20px; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px;" />
    </form>
    <form action="/top_resistants">
        <input type="submit" value="Voir les sensibilités des pokemons" style="background-color: green; color: white; font-size: 20px; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px;" />
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

@app.route("/pokemons_sensibilities")
def list_pokemons_sensibilities():

    # Requête ElasticSearch pour récupérer les Pokémons avec leurs sensibilités
    search_body = {
        "query": {"match_all": {}},
        "size": 1000,
        "_source": ["nom", "types", "sensibilities"]  # Utilisez "sensibilities" si c'est le nom dans Elasticsearch
    }
    search_result = es.search(index="pokemons", body=search_body)
    pokemons = search_result['hits']['hits']

    # Génération du HTML pour la liste des Pokémon avec leurs sensibilités
    pokemons_html = "<h1>Liste des Pokémons avec leurs sensibilités</h1><ul>"
    for pokemon in pokemons:
        name = pokemon['_source']['nom']
        types = ', '.join(pokemon['_source']['types'])
        sensibilities = pokemon['_source'].get('sensibilities', {})  # Utilisez "sensibilities" si c'est le nom dans Elasticsearch
        sensibilities_html = ', '.join([f"{key}: {value}" for key, value in sensibilities.items()])
        pokemons_html += f"<li>{name} - Types: {types} - Sensibilités: {sensibilities_html}</li>"
    pokemons_html += "</ul>"
    return pokemons_html

@app.route("/top_resistants")
def top_resistants():

    top_n = request.args.get('top', default=10, type=int)

    # Requête ElasticSearch pour récupérer les Pokémons avec leurs sensibilités et leurs types
    search_body = {
        "query": {"match_all": {}},
        "size": 1000,
        "_source": ["nom", "types", "sensibilities"]
    }
    search_result = es.search(index="pokemons", body=search_body)
    pokemons = search_result['hits']['hits']


    # Calcul du score de résistance pour chaque Pokémon et stockage des scores par type
    resistance_scores = []
    scores_by_type = {}
    for pokemon in pokemons:
        name = pokemon['_source']['nom']
        types = ", ".join(pokemon['_source']['types'])
        sensibilities = pokemon['_source'].get('sensibilities', {})
        resistance_score = sum(sensibilities.values())  # La somme des sensibilités

        # Ajouter le score à la liste des scores de résistance
        resistance_scores.append((name, types, resistance_score))

        # Stocker les scores par type pour analyse
        type_key = tuple(pokemon['_source']['types'])  # Un tuple pour gérer les types multiples
        if type_key not in scores_by_type:
            scores_by_type[type_key] = []
        scores_by_type[type_key].append(resistance_score)

    # Trier les Pokémon par leur score de résistance croissant
    top_resistant_pokemons = sorted(resistance_scores, key=lambda x: x[2])[:top_n]

    # Génération du HTML pour la liste des Pokémon les plus résistants
    top_resistants_html = "<h1>Top des Pokémon les moins sensibles</h1><ol>"
    for name, types, score in top_resistant_pokemons:  # Afficher seulement le top 10
        top_resistants_html += f"<li>{name} ({types}) - Score de résistance: {score:.2f}</li>"
    top_resistants_html += "</ol>"

    # Analyse des scores par type
    type_names = []
    avg_scores = []
    # Trier les types par le score moyen de résistance croissant
    sorted_types = sorted(scores_by_type.items(), key=lambda x: mean(x[1]))[:top_n]
    for type_key, scores in sorted_types:
        type_name = ", ".join(type_key)
        avg_score = mean(scores)
        type_names.append(type_name)
        avg_scores.append(avg_score)

    # Création de l'histogramme avec Plotly
    fig = px.bar(
        x=type_names,
        y=avg_scores,
        labels={"x": "Type", "y": "Score moyen de résistance"},
        title="Score moyen de résistance par type",
    )

    # Rendu de l'histogramme en HTML
    graph_html = pio.to_html(fig, full_html=False)

    top_resistants_html = """
    <form action="/top_resistants" method="get">
        <label for="top">Sélectionnez le nombre de résultats à afficher:</label>
        <select name="top" id="top" onchange="this.form.submit()">
            <option value="5">Top 5</option>
            <option value="10" selected>Top 10</option>
            <option value="15">Top 15</option>
            <option value="20">Top 20</option>
            <option value="30">Top 30</option>
            <option value="50">Top 50</option>
        </select>
    </form>
    """ + top_resistants_html

    # Intégrer l'histogramme dans le HTML de la page
    top_resistants_html += f"<h1>Score moyen des sensibilités par type par ordre croissant</h1>{graph_html}"

    return top_resistants_html


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


    