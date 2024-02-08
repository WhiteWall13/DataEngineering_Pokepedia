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

# Création d'une instance
es_indices = IndicesClient(es)

# Racine de l'applications web, permettant de se balader entre les différentes pages existantes
@app.route("/")
def home():
    index_name = "pokemons"
    total_pokemons = 0

    # Code de la page de chargement en attendant que les données soit prêtes
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
        # Pour savoir si notre base de données est prête il faut regarde si l'indice pokemon à été créé et compter ce nombre d'indices
        if es_indices.exists(index=index_name):
            count_result = es.count(index=index_name, body={"query": {"match_all": {}}})
            total_pokemons = count_result['count']
    except Exception : # Si une erreur est rencontrée : elasticsearch pas encore démarré ou index non créé
        return render_page
    
    if total_pokemons < 493 : # Si la base de données ne possède pas le nombre d'index suffisant mais que les index commence à être créé il ne faut pas encore rentré dans la page d'acceuil
        return render_page                
    else : # Page d'acceuil avec les boutons pour la navigation entre les différents onglets une fois elastic search avec nos données prêtes
        return render_template_string("""
        <html>
        <head>
            <style>
                body, html {
                    height: auto;
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
            <p>Bienvenu sur notre projet en Data Engineering sur pokepedia ! Vous pourrez trouver différentes exploitations des données des pokémon de la 1ère à la 4ème génération dans les boutons ci-dessous (accessibles avec les boutons)</p>
            <form action="/pokemons">
                <input type="submit" value="Voir les données des pokémon" " />
            </form>
            <form action="/statistiques">
                <input type="submit" value="Voir l'histogramme des types des pokémon" " />
            </form>
            <form action="/top_resistants">
                <input type="submit" value="Voir les sensibilités des pokémon"" />
            </form>
            <form action="/top_statistiques">
                <input type="submit" value="Voir les statistiques des pokémon"" />
            </form>
        </body>
        </html>
        """)


# Page des données extraites des pokemons, montrer la base de donnée utilisé
@app.route("/pokemons")
def list_pokemons():
    # Requête ElasticSearch pour compter le nombre total de Pokémon
    count_result = es.count(index="pokemons", body={"query": {"match_all": {}}})
    total_pokemons = count_result['count']

    # On récupère les sensibilités, types et images des pokemons de elastic search
    search_body = {
        "query": {"match_all": {}},
        "size": 1000,
        "_source": ["nom", "types", "sensibilities", "image", "stats"]
    }
    search_result = es.search(index="pokemons", body=search_body)
    
    # On cherche à preparer les données pour les afficher, retirer les éléments tel que les '' et les {}
    pokemon_data = [
        (
            pokemon['_source']['nom'],
            ", ".join(pokemon['_source']['types']),
            "; ".join(f"{key}: {value}" for key, value in pokemon['_source'].get('sensibilities', {}).items()),
            pokemon['_source'].get('image', ''),
            "; ".join(f"{key}: {value}" for key, value in pokemon['_source']['stats'].items())
        )
        for pokemon in search_result['hits']['hits']
    ]
                    
    # Page html pour afficher les données de chaque pokemon
    return render_template_string("""
        <html>
        <head>
            <style>
                body, html {
                    height: auto;
                    margin: 0;
                    padding: 0;
                    background-color: #353535;
                    color: #ffffff;
                    font-family: 'Arial', sans-serif;
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: space-around;
                }
                .pokemon-card {
                    background-color: #284b63;
                    border-radius: 30px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    padding: 20px;
                    margin: 10px;
                    text-align: center;
                }
                .pokemon-card img {
                    max-width: 150px;
                    height: auto;
                    margin-bottom: 10px;
                }
                .pokemon-card h3 {
                    color: #fff;
                    font-size: 24px;
                }
                .pokemon-card p {
                    color: #fff;
                }
            </style>
        </head>
        <body>
            <h2>Voici la liste des pokémon contenus dans la base de données ({{ total_pokemons }}) :</h2>
            <p> Toutes les données des pokémon ci-dessous sont extraites du site poképedia. Cette base de données comprend les pokémon de la 1ère à la 4ème génération.</p>
            {% for nom, types, sensibilities, image, stats in pokemon_data %}
                        <div class="pokemon-card">
                            <img src="{{ image }}" alt="Image de {{ nom }}">
                            <h3>{{ nom }}</h3>
                            <p>Types: {{ types }}</p>
                            <p>Sensibilités: {{ sensibilities }}</p>
                            <p>Statistiques: {{ stats }}</p>
                        </div>
                    {% endfor %}
            </div>
        </body>
        </html>
    """, total_pokemons= total_pokemons, pokemon_data= pokemon_data)

# Page pour afficher l'histogramme des nombre des types des pokemons 
@app.route('/statistiques')
def statistiques():
    
    # Requête à Elasticsearch pour récupérer les types des Pokémon 
    search_body = {
        "query": {"match_all": {}},
        "size": 1000,
        "_source": ["nom", "types"]
    }
    search_result = es.search(index="pokemons", body=search_body)
    
    # Traitement des résultats de la recherche pour calculer les scores de sensibilités et préparer les données de l'histogramme
    resistance_scores = [
        (
            pokemon['_source']['nom'],  # Nom du Pokémon
            ", ".join(pokemon['_source']['types']),  # Types du Pokémon
        )
        for pokemon in search_result['hits']['hits'] 
    ]

    # Préparation des données pour l'histogramme pour le comptage de type existant
    nombre_par_type = {}  # Dictionnaire pour stocker le nombre de Pokémon par type ou association de types
    for nom, types in resistance_scores:
        if types not in nombre_par_type:
            nombre_par_type[types] = 0  
        nombre_par_type[types] += 1
        
    types_pokemons = list(nombre_par_type.keys())
    comptage = list(nombre_par_type.values())

    # Création de l'histogramme avec Plotly
    fig = px.bar(
        x=types_pokemons,
        y=comptage,
        labels={"x": "Type", "y": "Nombre de pokémon de ce type"},
        title="Nombre de Pokémon par Type",
    )
    # Modification des couleurs de l'histogramme et ajouts des noms des axes et titres
    fig.update_layout(
        title_font_color="#ffffff",  
        title_font_size=24,  
        plot_bgcolor="#353535", 
        paper_bgcolor="#353535",  
        font_color="#ffffff", 
        xaxis_title="Type des Pokémon", 
        yaxis_title="Nombre de Pokémon de ce type",
        autosize=True,
    )

    # Rendu de l'histogramme en HTML
    graph_html = pio.to_html(fig, full_html=False)
    return render_template_string("""
            <html>
            <head>
                <style>
                    body, html {
                        height: auto;
                        margin: 0;
                        padding: 0;
                        background-color: #353535;
                        color: #ffffff;
                        font-family: 'Arial', sans-serif;
                    }
                </style>
            </head>
            <body>
                <h1>Voici la diversité du nombre de pokémon par types existants :</h1>
                <div>{{ graph_html|safe }}</div>      
            </body>
            </html>
            """, graph_html=graph_html)


# Page pour afficher le classement des sensibilités des pokemons et l'histogramme des sensibilités moyenne par association de type existants
@app.route("/top_resistants")
def top_resistants():
    # Menus déroulants pour afficher le nombre de pokemon issu du classement et le nombre de type à afficher pour l'histogramme
    top_n = request.args.get('top_n', default=10, type=int)
    histogram_n = request.args.get('histogram_n', default=10, type=int)

    # Requête à Elasticsearch pour récupérer les Pokémon avec leurs sensibilités, types et images
    search_body = {
        "query": {"match_all": {}},
        "size": 1000,
        "_source": ["nom", "types", "sensibilities", "image"]
    }
    search_result = es.search(index="pokemons", body=search_body)
    
    # Traitement des résultats de la recherche pour calculer les scores de sensibilités et préparer les données de l'histogramme
    resistance_scores = [
        (
            pokemon['_source']['nom'],  # Nom du Pokémon
            ", ".join(pokemon['_source']['types']),  # Types du Pokémon
            sum(pokemon['_source'].get('sensibilities', {}).values()),  # Calcul du score de sensibilités
            pokemon['_source'].get('image', '')  # URL de l'image du Pokémon
        )
        for pokemon in search_result['hits']['hits'] 
    ]

    # Tri score de sensibilités dans l'ordre croissant des pokemons (car plus un pokemon est resistant moin son score est élevé)
    top_resistant_pokemons = sorted(resistance_scores, key=lambda x: x[2])[:top_n]

    # Préparation des données pour l'histogramme
    scores_by_type = {}  # Dictionnaire pour stocker les scores par type
    for name, types, score, image_url in resistance_scores:
        # Pour chaque Pokémon, ajouter le score de sensibilités dans le dictionnaire avec la clé étant les types
        if types not in scores_by_type:
            scores_by_type[types] = []
        scores_by_type[types].append(score)

    # Préparation des données pour l'histogramme
    type_pokemon = []
    score_moyen = []

    # Trier les types par le score moyen de sensibilités croissant
    sorted_types = sorted(scores_by_type.items(), key=lambda x: mean(x[1]))[:histogram_n]

    # Génere le score moyen de résistances par associations de types existant
    for type_key, scores in sorted_types:
        type_name = type_key  
        score_type = mean(scores)
        type_pokemon.append(type_name)
        score_moyen.append(score_type)


    # Création de l'histogramme avec Plotly
    fig = px.bar(
        x=type_pokemon,
        y=score_moyen,
        labels={"x": "Type", "y": "Score moyen de sensibilités"},
        title="Score moyen de sensibilités par type",
    )
    # Modification des couleurs de l'histogramme et ajouts des noms des axes et titres
    fig.update_layout(
        title_font_color="#ffffff",  
        title_font_size=24,  
        plot_bgcolor="#353535", 
        paper_bgcolor="#353535",  
        font_color="#ffffff", 
        xaxis_title="Types des pokémon", 
        yaxis_title="Valeur des sensibilités moyenne",
        autosize=True,
    )

    # Conversion de l'histogramme en HTML pour l'intégrer dans la page web
    graph_html = pio.to_html(fig, full_html=False)

    # Génération du HTML pour les menus déroulants, la liste des Pokémon les plus résistants et l'histogramme des scores par associations de types existants
    return render_template_string("""
        <html>
        <head>
            <style>
                body, html {
                    height: auto;
                    margin: 0;
                    padding: 0;
                    background-color: #353535;
                    color: #ffffff;
                    font-family: 'Arial', sans-serif;
                    text-align: center;
                }
                h1, h2 {
                    font-size: 2.5em;
                    margin: 20px 0;
                }
                form {
                    margin: 20px auto;
                    display: block;
                }
                ol {
                    padding: 0;
                    list-style-type: none;
                }
                ol li {
                    margin: 10px 0;
                }
                .pokemon-card {
                    background-color: #284b63; 
                    border-radius: 20px; 
                    padding: 10px; 
                    margin: 10px; 
                    text-align: center; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
                    display: inline-block; 
                    width: 200px; 
                }
                .pokemon-card img {
                    width: 100px; 
                    height: auto; 
                }
                .pokemon-card h3 {
                    font-size: 1.2em; 
                }
                .pokemon-card p {
                    font-size: 0.9em;
                }
                .pokemon-rank {
                    font-size: 2em; 
                }
                p {
                    font-size: 1.5em;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
        <h1>Classement des Pokémon les moins sensibles</h1>
        <p> Le classement est établi sur la base des sensibilités des pokémon. Chaque pokémon possède des sensibilités à des types, ce classement réalise la somme des sensibilités (ex : au type Plante, Feu....) pour établir un score de sensibilité. Les pokémon de ce top sont les pokémon considérés comme les plus résistants de par la nature de leur type.</p>
        <div>
        <form action="{{ url_for('top_resistants') }}" method="get">
            <label for="top_n">Choisir le nombre de pokémon à afficher (trié par ordre croissant):</label>
            <select name="top_n" id="top_n" onchange="this.form.submit()">
                {% for i in [5, 10, 20, 30, 50] %}
                    <option value="{{ i }}" {{ 'selected' if i == top_n else '' }}>{{ i }}</option>
                {% endfor %}
            </select>
            <br>
            <ol>
                <div>
                    {% for name, types, score, image_url in top_resistant_pokemons %}
                        <div class="pokemon-card">
                            <span class="pokemon-rank">#{{ loop.index }}</span>
                            <img src="{{ image_url }}" alt="Image de {{ name }}">
                            <h3>{{ name }}</h3>
                            <p>Types: {{ types }}</p>
                            <p>Score de sensibilités: {{ score }}</p>
                        </div>
                    {% endfor %}
                </div>
            </ol>
            <h2>Score moyen de sensibilités par type</h2>
            <p> L'histogramme représente le score moyen obtenu par chaque association de type existant (moyenne des sensibilités de chaque pokémon de ces types).<p>
            <div>
            <label for="histogram_n">Choisir le nombre de types affichés dans l'histogramme (trié par ordre croissant):</label>
            <select name="histogram_n" id="histogram_n" onchange="this.form.submit()">
                {% for i in [5, 10, 20, 30, 50] %}
                    <option value="{{ i }}" {{ 'selected' if i == histogram_n else '' }}>{{ i }}</option>
                {% endfor %}
            </select>
            </form>
            </div>
            <div>{{ graph_html|safe }}</div>    
        </body>
        </html>
        """, graph_html=graph_html, top_n=top_n, histogram_n=histogram_n, top_resistant_pokemons=top_resistant_pokemons[:top_n])

# Page pour afficher les classements des pokemons selon la statistique et le type choisi
@app.route("/top_statistiques")
def top_statistiques():

    # Menus déroulants pour afficher le nombre de pokemon issu du classement et le nombre de type à afficher pour l'histogramme
    top_n = request.args.get('top_n', default=10, type=int)
    histogram_n = request.args.get('histogram_n', default=10, type=int)

    # Menus déroulants pour selectionner le type et la statistique désiré pour le classement et la statistique pour l'histogramme
    selected_type = request.args.get('type', default='Feu', type=str)
    selected_stat = request.args.get('stat', default='Attaque', type=str)

    # Requête à Elasticsearch pour récupérer les Pokémon avec leurs statistiques et types
    search_body = {
        "query": {"match_all": {}},
        "size": 1000,
        "_source": ["nom", "types", "image", "stats"]
    }
    search_result = es.search(index="pokemons", body=search_body)

    # On prepare les données pour le classement des pokemons suivant le type et la statistique choisie
    statistiques = [
        (
            pokemon['_source']['nom'],
            ", ".join(pokemon['_source']['types']),
            pokemon['_source'].get('image', ''),
            pokemon['_source']['stats'][selected_stat]  
        )
        for pokemon in search_result['hits']['hits'] 
        if selected_type in pokemon['_source']['types']
    ]

    # Tri par statistique, en ordre décroissant
    top_statistiques_pokemons = sorted(statistiques, key=lambda x: x[3], reverse=True)[:top_n] 

    # On prepare les données pour l'histogramme des pokemons suivant la statique choisi, cet histogramme doit contenir toutes les associations de type possible
    statistiques_pokemons = [
        (
            pokemon['_source']['nom'],
            ", ".join(pokemon['_source']['types']),
            pokemon['_source'].get('image', ''),
            pokemon['_source']['stats'][selected_stat] 
        )
        for pokemon in search_result['hits']['hits'] 
    ]

    # Préparation des données pour l'histogramme
    scores_by_type = {}  # Dictionnaire pour stocker les scores par type
    for name, types, image_url, stats in statistiques_pokemons: # Pour chaque pokemon on extrait son score de résistance et on l'associe à la clef des types
        if types not in scores_by_type:
            scores_by_type[types] = []
        scores_by_type[types].append(stats)

    # Préparation des données pour l'histogramme
    type_pokemon = []
    score_moyen = []

    # Trier les types par le score moyen de résistance croissant
    sorted_types = sorted(scores_by_type.items(), key=lambda x: mean(x[1]),reverse=True)[:histogram_n]

    # Calcul les scores moyens par type
    for type_key, scores in sorted_types:
        type_name = type_key  
        score_pokemon = mean(scores)
        type_pokemon.append(type_name)
        score_moyen.append(score_pokemon)


    # Création de l'histogramme avec Plotly
    fig = px.bar(
        x=type_pokemon,
        y=score_moyen,
        labels={"x": "Type", "y": "Score moyen de "+selected_stat},
        title="Score moyen de la statistique "+selected_stat+" par type",
    )
    fig.update_layout(
        title_font_color="#ffffff",  
        title_font_size=24,  
        plot_bgcolor="#353535", 
        paper_bgcolor="#353535",  
        font_color="#ffffff", 
        xaxis_title="Types des pokémon", 
        yaxis_title="Valeur "+selected_stat+" moyenne ",
        autosize=True,
    )

    # Conversion de l'histogramme en HTML pour l'intégrer dans la page web
    graph_html = pio.to_html(fig, full_html=False)


    # Générer le HTML pour les menus déroulants
    return render_template_string("""
        <html>
        <head>
            <style>
                body, html {
                    height: auto;
                    margin: 0;
                    padding: 0;
                    background-color: #353535;
                    color: #ffffff;
                    font-family: 'Arial', sans-serif;
                    text-align: center;
                }
                h1, h2 {
                    font-size: 2.5em;
                    margin: 20px 0;
                }
                p {
                    font-size: 1.5em;
                    margin: 20px 0;
                }
                .pokemon-card {
                    background-color: #284b63; 
                    border-radius: 20px; 
                    padding: 10px; 
                    margin: 10px; 
                    text-align: center; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
                    display: inline-block; 
                    width: 200px; 
                }
                .pokemon-card img {
                    width: 100px; 
                    height: auto; 
                }
                .pokemon-card h3 {
                    font-size: 1.2em; 
                }
                .pokemon-card p {
                    font-size: 0.9em;
                }
                .pokemon-rank {
                    font-size: 2em; 
                }
                select {
                    font-size: 20px;
                    padding: 10px;
                    margin-bottom: 20px;
                }
                form {
                    margin: 20px auto;
                    display: block;
                }
                ol {
                    padding: 0;
                    list-style-type: none;
                }
            </style>
        </head>
        <body>
        <div>
            <h1>Classement des Pokémon selon leurs statistiques</h1>
            <p> Le classement permet d'établir les pokémon les plus forts selon les paramètres choisis. Un classement idéal pour compléter votre équipe de pokémon selon votre besoin.</p>
            </div>
            <div>
            <form action="{{ url_for('top_statistiques') }}" method="get">
                <label for="top_n">Choisir le nombre de pokémon à afficher :</label>
                <select name="top_n" id="top_n" onchange="this.form.submit()">
                    {% for i in [5, 10, 20, 30, 50] %}
                        <option value="{{ i }}" {{ 'selected' if i == top_n else '' }}>{{ i }}</option>
                    {% endfor %}
                </select>
                <label for="type">Choisir le type de Pokémon :</label>
                <select name="type" id="type" onchange="this.form.submit()">
                    {% for i in ["Normal", "Plante", "Feu", "Eau", "Électrik", "Glace","Combat","Poison","Sol","Vol","Psy","Insecte","Roche","Spectre","Dragon","Ténèbres","Acier","Fée"] %}
                        <option value="{{ i }}" {{ 'selected' if i == selected_type else '' }}>{{ i }}</option>
                    {% endfor %}
                </select>        
                <label for="stat">Choisir la statistique :</label>
                <select name="stat" id="stat" onchange="this.form.submit()">
                    {% for i in ["PV", "Attaque", "Défense", "Attaque Spéciale", "Défense Spéciale", "Vitesse", "Spécial"] %}
                        <option value="{{ i }}" {{ 'selected' if i == selected_stat else '' }}>{{ i }}</option>
                    {% endfor %}
                </select>
            
            </div>    
            <ol> 
                <div>
                        {% for name, types, image_url, stats in top_statistiques_pokemons %}
                            <div class="pokemon-card">
                                <span class="pokemon-rank">#{{ loop.index }}</span>
                                <img src="{{ image_url }}" alt="Image de {{ name }}">
                                <h3>{{ name }}</h3>
                                <p>Types: {{ types }}</p>
                                <p>Statistique: {{ stats }}</p>
                            </div>
                        {% endfor %}
                    </div>
            </ol> 
        <h2>Score moyen de la statistique {{ selected_stat }} par type</h2>
        <p> Cet histogramme présente le score moyen obtenu par chaque association de type de pokémon. Permettant de déterminer les associations de types de pokémon qui contiennent les pokémon les plus forts suivant la statistique choisie.</p>
            <div>
            <label for="histogram_n">Choisir le nombre de types à afficher dans l'histogramme :</label>
            <select name="histogram_n" id="histogram_n" onchange="this.form.submit()">
                {% for i in [5, 10, 20, 30, 50] %}
                    <option value="{{ i }}" {{ 'selected' if i == histogram_n else '' }}>{{ i }}</option>
                {% endfor %}
            </select>
            </form>
            </div>
            <div>{{ graph_html|safe }}</div>   
        </body>
        </html>
    """, top_n=top_n, selected_stat=selected_stat, selected_type=selected_type, top_statistiques_pokemons=top_statistiques_pokemons[:top_n],graph_html=graph_html,histogram_n=histogram_n)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
