import psycopg2
import json
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def insert_pokemon_data(json_data, db_params):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # SQL queries to insert data into tables
        insert_pokemon = sql.SQL(
            "INSERT INTO pokemon (numero, nom, image_mini, lien, image) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (numero) DO NOTHING;"
        )
        insert_type = sql.SQL(
            "INSERT INTO type (type_nom) VALUES (%s) ON CONFLICT (type_nom) DO NOTHING;"
        )
        insert_pokemon_type = sql.SQL(
            "INSERT INTO pokemon_type (numero, type_id) VALUES (%s, (SELECT type_id FROM type WHERE type_nom = %s)) ON CONFLICT DO NOTHING;"
        )
        insert_stats = sql.SQL(
            "INSERT INTO statistiques (numero, pv, attaque, defense, attaque_speciale, defense_speciale, vitesse, special) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (numero) DO NOTHING;"
        )
        insert_evolution = sql.SQL(
            "INSERT INTO evolution (numero, evolution) VALUES (%s, %s) ON CONFLICT DO NOTHING;"
        )

        # Iterate over the JSON data and insert into tables
        for pokemon in json_data:
            # print(pokemon["nom"])
            # Insert into pokemon table
            cur.execute(
                insert_pokemon,
                (
                    pokemon["numero"],
                    pokemon["nom"],
                    pokemon["image_mini"],
                    pokemon["lien"],
                    pokemon["image"],
                ),
            )

            # Insert types and pokemon types
            for type_name in pokemon["types"]:
                cur.execute(insert_type, (type_name,))
                cur.execute(insert_pokemon_type, (pokemon["numero"], type_name))

            # Insert stats
            stats = pokemon["stats"]
            cur.execute(
                insert_stats,
                (
                    pokemon["numero"],
                    stats["PV"],
                    stats["Attaque"],
                    stats["Défense"],
                    stats["Attaque Spéciale"],
                    stats["Défense Spéciale"],
                    stats["Vitesse"],
                    stats.get("Spécial"),
                ),
            )

            # Insert evolutions
            for evolution in pokemon["evolutions"]:
                cur.execute(insert_evolution, (pokemon["numero"], evolution))

        # Close the database connection
        cur.close()
        conn.close()
        return "Data insertion successful."
    except Exception as e:
        return str(e)


# Database parameters
db_params = {
    "dbname": "pokepedia_db",
    "user": "user",
    "password": "password",
    "host": "postgres_pokepedia",
    "port": "5432",
}

# JSON file path
json_file_path = "/app/data/pokemons.json"

# Load data from JSON file
with open(json_file_path, "r") as file:
    pokemons_data = json.load(file)

# Uncomment below line to execute the insertion (after filling db_params)
insert_pokemon_data(pokemons_data, db_params)
