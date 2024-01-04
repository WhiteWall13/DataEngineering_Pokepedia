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

    # Requête pour récupérer les données de PostgreSQL
    query = '''
    SELECT nom, array_agg(DISTINCT type_nom) as types
    FROM pokemon
    JOIN pokemon_type ON pokemon.numero = pokemon_type.numero
    JOIN type ON pokemon_type.type_id = type.type_id
    GROUP BY pokemon.nom;
    '''
    
    cursor.execute(query)
    rows = cursor.fetchall()

    actions = [
        {
            "_index": "pokemons",
            "_id": row[0],  # Utiliser le nom du Pokémon comme identifiant unique
            "_source": {
                "nom": row[0],
                "types": row[1],
            },
        }
        for row in rows
    ]

    helpers.bulk(es, actions)
    cursor.close()
    conn.close()

# Exécuter le transfert
transfer_data()
