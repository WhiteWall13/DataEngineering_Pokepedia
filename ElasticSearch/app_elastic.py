import psycopg2
from elasticsearch import Elasticsearch, helpers

# Connexion à PostgreSQL
def connect_postgres():
    try:
        return psycopg2.connect(
            host="db",
            database="pokepedia_db",
            user="user",
            password="password")
    except psycopg2.DatabaseError as error:
        print(error)

# Connexion à Elasticsearch
es = Elasticsearch(
    ["http://elasticsearch:9200"],
    basic_auth=('elastic', 'password'),
)

# Fonction pour transférer les données
def transfer_data():
    conn = connect_postgres()
    cursor = conn.cursor()

    # Requête pour récupérer les noms et les types de Pokémon
    query_types = '''
    SELECT nom, array_agg(DISTINCT type_nom) as types
    FROM pokemon
    JOIN pokemon_type ON pokemon.numero = pokemon_type.numero
    JOIN type ON pokemon_type.type_id = type.type_id
    GROUP BY pokemon.nom;
    '''
    cursor.execute(query_types)
    pokemons_types = cursor.fetchall()

    # Requête pour récupérer les sensibilités de Pokémon
    query_sensibilities = '''
    SELECT p.nom, json_object_agg(t.type_nom, s.valeur) as sensibilites
    FROM pokemon p
    JOIN pokemon_sensibilite ps ON p.numero = ps.numero
    JOIN type t ON ps.type_id = t.type_id
    JOIN sensibilite s ON ps.sensibilite_id = s.sensibilite_id
    GROUP BY p.nom;
    '''
    cursor.execute(query_sensibilities)
    pokemons_sensibilities = cursor.fetchall()

    # Créer un dictionnaire pour les sensibilités pour un accès facile
    sensibilities_dict = {row[0]: row[1] for row in pokemons_sensibilities}

    # Préparez les actions pour le transfert de données
    actions = [
        {
            "_index": "pokemons",
            "_id": pokemon[0],  # Utiliser le nom du Pokémon comme identifiant unique
            "_source": {
                "nom": pokemon[0],
                "types": pokemon[1],
                "sensibilities": sensibilities_dict.get(pokemon[0], {})  
            },
        }
        for pokemon in pokemons_types
    ]

    # Transfert en masse vers Elasticsearch
    helpers.bulk(es, actions)
    cursor.close()
    conn.close()

# Exécutez le transfert
transfer_data()