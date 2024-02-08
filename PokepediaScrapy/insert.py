import psycopg2
import json
import logging
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Fonction pour les statistiques de pichu
def pichu_stats():
    return {
        "PV": 20,
        "Attaque": 40,
        "Défense": 15,
        "Attaque Spéciale": 35,
        "Défense Spéciale": 35,
        "Vitesse": 60,
    }

# Fonction pour les valeurs des sensibilités de pichu
def pichu():
    return{
        "Normal": 1,
        "Plante": 2,
        "Feu": 1,
        "Eau": 1,
        "Électrik": 1,
        "Glace": 1,
        "Combat": 1,
        "Poison": 1,
        "Sol": 2,
        "Vol": 0.5,
        "Psy": 1,
        "Insecte": 1,
        "Roche": 1,
        "Spectre": 1,
        "Dragon": 1,
        "Ténèbres": 1,
        "Acier": 0.5,
        "Fée": 1
    }

# Vérifier le format du json contenant les données scrapé
def validate_data(json_data):
    """Validates the JSON data to ensure it is in the expected format"""
    for entry in json_data:
        if not all(
            key in entry
            for key in [
                "numero",
                "nom",
                "types",
                "image_mini",
                "lien",
                "image",
                "stats",
                "evolutions",
                "sensibilities"
            ]
        ):
            logging.error(f"Invalid JSON data format for entry: {entry}")
            return False
    return True


# Insertion des données extraites dans le json 
def insert_pokemon_data(json_data, db_params):
    
    # On ajoute les données seulement si le format est correct
    if not validate_data(json_data):
        logging.error("Invalid JSON data format")
        return

    try:
        # Connexion la base de données SQL PostgreSQL 
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Compte le nombre d'objects dans le json
        total_objects = len(json_data)
        logging.info(f"Number of objects in JSON data: {total_objects}")

        # Requetes SQL pour insérer les données dans la base de données
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
            "INSERT INTO statistiques (numero, pv, attaque, defense, attaque_speciale, defense_speciale, vitesse, special) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;"
        )


        # On insere les donnés dans la base de données
        for pokemon in json_data:
            cur.execute(
                insert_pokemon,
                (
                    pokemon["numero"],
                    pokemon["nom"],
                    pokemon["image_mini"],
                    pokemon["lien"],
                    pokemon["image"]
                ),
            )
            # Insertion des types de Pokémon et création des associations avec le Pokémon
            for type in pokemon["types"]:
                cur.execute(insert_type, (type,))
                cur.execute(insert_pokemon_type, (pokemon["numero"], type))
            
            # Gestion pour Pichu
            if pokemon["numero"] == 172:
                pokemon["sensibilities"] = pichu()
                pokemon["stats"] = pichu_stats()
                
            # Insertion des statistiques du Pokémon s'il n'en a pas
            if pokemon["stats"] == {}:
                pokemon["stats"]["PV"] = 0
                pokemon["stats"]["Attaque"] = 0
                pokemon["stats"]["Défense"] = 0
                pokemon["stats"]["Attaque Spéciale"] = 0
                pokemon["stats"]["Défense Spéciale"] = 0
                pokemon["stats"]["Vitesse"] = 0
                print(f"Stats not found for pokemon: {pokemon['nom']}")
            # Insertion des statistiques du Pokémon
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
            # Insertion des sensibilités du Pokémon si elles existent
            if 'sensibilities' in pokemon:
                for type_name, value in pokemon['sensibilities'].items():
                    # Vérifie si le type existe déjà et obtient son id, sinon l'insère
                    cur.execute("SELECT type_id FROM type WHERE type_nom = %s;", (type_name,))
                    type_id_result = cur.fetchone()
                    if not type_id_result:
                        cur.execute("INSERT INTO type (type_nom) VALUES (%s) RETURNING type_id;", (type_name,))
                        type_id = cur.fetchone()[0]
                    else:
                        type_id = type_id_result[0]
                    
                    # Vérifie si la sensibilité existe déjà et obtient son id, sinon l'insère
                    cur.execute("SELECT sensibilite_id FROM sensibilite WHERE valeur = %s;", (value,))
                    sensibilite_id_result = cur.fetchone()
                    if not sensibilite_id_result:
                        cur.execute("INSERT INTO sensibilite (valeur) VALUES (%s) RETURNING sensibilite_id;", (value,))
                        sensibilite_id = cur.fetchone()[0]
                    else:
                        sensibilite_id = sensibilite_id_result[0]
                    
                    # Insérer la liaison entre pokemon, type et sensibilité
                    cur.execute(
                        "INSERT INTO pokemon_sensibilite (numero, type_id, sensibilite_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                        (pokemon["numero"], type_id, sensibilite_id)
                    )

            
        # Enregistrement pour montrer que la abse de donnée est prête
        logging.info("Data insertion completed successfully.")

    # Si une erreur arrive alors la signaler
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    # Fermeture de la connexion à la base de données
    finally:
        if conn:
            cur.close()
            conn.close()
            logging.info("Database connection closed.")


# Paramêtres de la base de données SQL
db_params = {
    "dbname": "pokepedia_db",
    "user": "user",
    "password": "password",
    "host": "postgres_pokepedia",
    "port": "5432",
}

# Chemin du fichier json
json_file_path = "/app/data/pokemons.json"

# Chargement des données du json
with open(json_file_path, "r") as file:
    pokemons_data = json.load(file)

insert_pokemon_data(pokemons_data, db_params)
