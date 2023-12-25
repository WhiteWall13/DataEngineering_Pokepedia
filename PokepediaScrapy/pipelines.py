# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import json
import os

from scrapy.exporters import JsonItemExporter
import psycopg2
from scrapy.exceptions import DropItem


class PokemonPipeline:
    def open_spider(self, spider):
        os.makedirs("../data", exist_ok=True)
        try:
            self.file = open("../data/pokemons.json", "rb+")
        except FileNotFoundError:
            self.file = open("../data/pokemons.json", "w+b")
        try:
            self.data = json.load(self.file)
        except json.JSONDecodeError:
            self.data = []
        self.file.seek(0)

    def close_spider(self, spider):
        exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        exporter.start_exporting()
        for item in self.data:
            exporter.export_item(item)
        exporter.finish_exporting()
        self.file.truncate()
        self.file.close()

    def process_item(self, item, spider):
        for existing_item in self.data:
            if existing_item["numero"] == item["numero"]:
                existing_item.update(item)
                break
        else:
            self.data.append(item)
        return item


# class PostgresPipeline(object):
#     def open_spider(self, spider):
#         self.connection = psycopg2.connect(
#             host="db",
#             database="pokepedia_db",
#             user="user",
#             password="password",
#         )
#         self.cursor = self.connection.cursor()

#     def close_spider(self, spider):
#         self.connection.commit()
#         self.cursor.close()
#         self.connection.close()

#     def process_item(self, item, spider):
#         print(item)
#         try:
#             # Insérer les données de base du Pokémon
#             self.cursor.execute(
#                 "INSERT INTO pokemon (numero, nom, image_mini, lien, image) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (numero) DO NOTHING;",
#                 (
#                     item["numero"],
#                     item["nom"],
#                     item["image_mini"],
#                     item["lien"],
#                     item["image"],
#                 ),
#             )

#             # Insérer les types de Pokémon
#             for type in item["types"]:
#                 self.cursor.execute(
#                     "INSERT INTO type (type_nom) VALUES (%s) ON CONFLICT (type_nom) DO NOTHING;",
#                     (type,),
#                 )
#                 self.cursor.execute(
#                     "INSERT INTO pokemon_type (numero, type_id) SELECT %s, type_id FROM type WHERE type_nom = %s ON CONFLICT DO NOTHING;",
#                     (item["numero"], type),
#                 )

#             # Insérer les statistiques de Pokémon
#             stats = item["stats"]
#             self.cursor.execute(
#                 "INSERT INTO statistiques (numero, pv, attaque, defense, attaque_speciale, defense_speciale, vitesse, special) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (numero) DO NOTHING;",
#                 (
#                     item["numero"],
#                     stats["PV"],
#                     stats["Attaque"],
#                     stats["Défense"],
#                     stats["Attaque Spéciale"],
#                     stats["Défense Spéciale"],
#                     stats["Vitesse"],
#                     stats["Spécial"],
#                 ),
#             )

#             # Insérer les évolutions de Pokémon
#             for evolution in item["evolutions"]:
#                 self.cursor.execute(
#                     "INSERT INTO evolution (numero, evolution) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
#                     (item["numero"], evolution),
#                 )

#         except psycopg2.DatabaseError as e:
#             raise DropItem(f"Erreur lors de l'insertion dans la base de données : {e}")

#         return item
