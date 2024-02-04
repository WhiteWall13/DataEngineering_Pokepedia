from flask import Flask, render_template_string
import plotly.express as px
import plotly.io as pio
from statistics import mean
from flask import request
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.client import IndicesClient

app = Flask(__name__)

# Connexion à Elasticsearch
es = Elasticsearch(
    ["http://elasticsearch:9200"],
    basic_auth=('elastic', 'password'),
)

# Création d'une instance de la classe IndicesClient
es_indices = IndicesClient(es)

@app.route("/")
def home():
    index_name = "pokemons"
    total_pokemons = 0

    # Page de chagrment, pour faire patientez l'utilisateur en attendant que les données soit prêtes
    render_page = render_template_string("""
        <html>
        <head>
            <meta http-equiv="refresh" content="5">
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #353535;
                    color: #ffffff; 
                }
                img {
                    max-width: 80%;
                    height: auto;
                    display: block;
                    margin: 0 auto; 
                    margin-bottom: 20px;
                }
                p {
                    font-size: 24px; 
                    margin-bottom: 30px; 
                    color: #ffffff; 
                }
            </style>
        </head>
        <body>
            <div style="text-align: center; padding: 50px;">
                <img src="{{ url_for('static', filename='Assets/pokeball_chargement.gif') }}" alt="Chargement des données">
                <p>Bienvenue sur notre projet en Data Engineering sur pokepedia ! La base de données est en train de charger, veuillez patienter. Cette page se rafraîchira automatiquement toutes les 5 secondes.</p>
            </div>
        </body>
        </html>
        """)

    try:
        # vérifi si l'index pokemon existe
        if es_indices.exists(index=index_name):
            count_result = es.count(index=index_name, body={"query": {"match_all": {}}})
            total_pokemons = count_result['count']
    except Exception : # Si une erreur est rencontrée : elasticsearch pas encore démarré ou index non créé
        return render_page
    
    if total_pokemons < 493 : # Si la base de données ne possède pas le nombre de pokemon suffisant mais que l'index est créé
        return render_page                
    else : # Page d'acceuil avec les boutons pour la navigation entre les différents onglets une fois elastic search prêt
        return render_template_string("""
        <html>
        <head>
            <style>
                body, html {
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    background-color: #353535;
                    color: #ffffff;
                    font-family: 'Arial', sans-serif;
                }
                img {
                    max-width: 80%;
                    height: auto;
                    margin-bottom: 20px;
                }
                p {
                    font-size: 30px;
                    margin-bottom: 30px;
                    color: #ffffff; 
                    max-width: 1400px; 
                }
                form {
                    margin: 10px 0;
                    text-align: center;
                }
                input[type=submit] {
                    background-color: #284b63;
                    color: #ffffff;
                    font-size: 25px;
                    padding: 30px 60px;
                    border: none;
                    border-radius: 30px;
                    cursor: pointer;
                    margin: 10px auto;
                    display: block;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }
            </style>
        </head>
        <body>
            <img src="{{ url_for('static', filename='Assets/Data-Engineering.png') }}" alt="Data Engineering">
            <p>Bienvenu sur notre projet en Data Engineering sur pokepedia ! Vous pourrez trouver différentes exploitations des données des pokémons dans les menus ci-dessous (accessible avec les boutons)</p>
            <form action="/pokemons">
                <input type="submit" value="Voir les Pokémons" " />
            </form>
            <form action="/statistiques">
                <input type="submit" value="Voici les statistiques des pokémons" " />
            </form>
            <form action="/pokemons_sensibilities">
                <input type="submit" value="Voir les Pokémons et leurs sensibilités"" />
            </form>
            <form action="/top_resistants">
                <input type="submit" value="Voir les sensibilités des pokemons"" />
            </form>
        </body>
        </html>
        """)






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
    # Récupérer les valeurs sélectionnées pour les menus déroulants ou définir la valeur par défaut si non fournies
    top_n = request.args.get('top_n', default=10, type=int)
    histogram_n = request.args.get('histogram_n', default=10, type=int)

    # Requête à Elasticsearch pour récupérer les Pokémon avec leurs sensibilités, types et images
    search_body = {
        "query": {"match_all": {}},
        "size": 1000,
        "_source": ["nom", "types", "sensibilities", "image"]
    }
    search_result = es.search(index="pokemons", body=search_body)
    
    # Traitement des résultats de la recherche pour calculer les scores de résistance et préparer les données de l'histogramme
    resistance_scores = [
        (
            pokemon['_source']['nom'],  # Nom du Pokémon
            ", ".join(pokemon['_source']['types']),  # Types du Pokémon
            sum(pokemon['_source'].get('sensibilities', {}).values()),  # Calcul du score de sensibilités
            pokemon['_source'].get('image', '')  # URL de l'image du Pokémon
        )
        for pokemon in search_result['hits']['hits'] 
    ]

    # Tri des Pokémon par leur score de résistance dans l'ordre croissant
    top_resistant_pokemons = sorted(resistance_scores, key=lambda x: x[2])[:top_n]

    # Préparation des données pour l'histogramme
    scores_by_type = {}  # Dictionnaire pour stocker les scores par type
    for name, types, score, image_url in resistance_scores:
        # Pour chaque Pokémon, ajouter le score de résistance dans le dictionnaire avec la clé étant les types
        if types not in scores_by_type:
            scores_by_type[types] = []
        scores_by_type[types].append(score)

    # Préparation des données pour l'histogramme
    type_names = []
    avg_scores = []

    # Trier les types par le score moyen de résistance croissant
    sorted_types = sorted(scores_by_type.items(), key=lambda x: mean(x[1]))[:histogram_n]

    for type_key, scores in sorted_types:
        # Pas besoin de joindre ici si type_key est déjà une chaîne
        type_name = type_key  
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

    # Conversion de l'histogramme en HTML pour l'intégrer dans la page web
    graph_html = pio.to_html(fig, full_html=False)

    # Génération du HTML pour les menus déroulants, la liste des Pokémon les plus résistants et l'histogramme
    return render_template_string("""
    <h1>Top des Pokémon les moins sensibles</h1>
    <form action="{{ url_for('top_resistants') }}" method="get">
        <label for="top_n">Choisir le nombre de pokemons à affiché (trié par ordre croissant):</label>
        <select name="top_n" id="top_n" onchange="this.form.submit()">
            {% for i in [5, 10, 20, 30, 50] %}
                <option value="{{ i }}" {{ 'selected' if i == top_n else '' }}>{{ i }}</option>
            {% endfor %}
        </select>
        <br>
        <ol>
        {% for name, types, score, image_url in top_resistant_pokemons %}
            <li>
                <img src="{{ image_url }}" alt="Image de {{ name }}" style="width:100px; height:auto;">
                {{ name }} ({{ types }}) - Score de résistance: {{ score }}
            </li>
        {% endfor %}
        </ol>
        <h2>Score moyen de résistance par type</h2>
        <label for="histogram_n">Choisir le nombre de type affiché dans l'histogramme (trié par ordre croissant):</label>
        <select name="histogram_n" id="histogram_n" onchange="this.form.submit()">
            {% for i in [5, 10, 20, 30, 50] %}
                <option value="{{ i }}" {{ 'selected' if i == histogram_n else '' }}>{{ i }}</option>
            {% endfor %}
        </select>
    </form>
    {{ graph_html|safe }}
    """, top_n=top_n, histogram_n=histogram_n, top_resistant_pokemons=top_resistant_pokemons[:top_n], graph_html=graph_html)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


    