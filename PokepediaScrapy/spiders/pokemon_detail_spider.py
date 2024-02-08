import scrapy
import json
from PokepediaScrapy.items import PokemonItem


class PokemonDetailSpider(scrapy.Spider):
    name = "pokemon_detail"

    def start_requests(self):
        with open("../data/pokemons.json", "r") as file:
            pokemons = json.load(file)
            for pokemon in pokemons:
                yield scrapy.Request(
                    url=pokemon["lien"],
                    callback=self.parse,
                    meta={"pokemon_item": pokemon},
                )

    def parse(self, response):
        pokemon_item = response.meta["pokemon_item"]

        # Extractions des url des images des pokemons
        image_url = response.xpath(
            "//span[@typeof='mw:File']/a[@class='mw-file-description']/img/@src"
        ).get()
        if image_url:
            pokemon_item["image"] = response.urljoin(image_url)

        # Extractions des statistiques des pokemons
        stats = {}
        # Sélectionner les tableaux qui contiennent "Statistiques indicatives" dans l'en-tête
        tables = response.xpath(
            "//th[contains(text(), 'Statistiques indicatives')]/ancestor::table"
        )
        # Recupère chaque valeur et sa statistique 
        for table in tables:
            for stat_row in table.xpath("./tbody/tr"):
                stat_name = stat_row.xpath("td[1]/a/text()").get()
                stat_value = stat_row.xpath("td[2]/text()").get()

                if stat_name and stat_value:
                    stats[stat_name.strip()] = int(stat_value.strip())

        pokemon_item["stats"] = stats

        # Extractions des Sensibilités
        sensibilities = {}

        # Tableau des sensibilités
        sensibilities_table = response.xpath('//table[contains(@class, "sensibilite")]')

        # Parcour chaque type et on extrait le type et la sensibilité correspondante
        for sensibility_cell in sensibilities_table.xpath('.//tr[@class="ligne-efficacités"]/td'):
            # Extraction du nom du type sans "(type)"
            type_name = sensibility_cell.xpath('.//a/@title').get().replace(" (type)", "")

            # Extraction de la sensibilité
            sensibility_value_raw = sensibility_cell.xpath('.//div/text()').get()
            
            # Gérer les cas où la div de sensibilité est vide (sensibilité standard de 1)
            if not sensibility_value_raw:
                sensibilities[type_name.strip()] = 1.0
            else:
                # Nettoyer la valeur brute
                sensibility_value_raw = sensibility_value_raw.strip()  # Enlever les espaces blancs autour de la valeur

                # Convertir la valeur de sensibilité en nombre
                sensibility_value = None
                if sensibility_value_raw == '× ¼':
                    sensibility_value = 0.25
                elif sensibility_value_raw == '× ½':
                    sensibility_value = 0.5
                elif sensibility_value_raw == '× 2':
                    sensibility_value = 2.0
                elif sensibility_value_raw == '× 4':
                    sensibility_value = 4.0
                elif sensibility_value_raw == '× 0': 
                    sensibility_value = 0.0

                # Enregistrer la valeur de sensibilité
                if sensibility_value is not None:
                    sensibilities[type_name.strip()] = sensibility_value

        pokemon_item["sensibilities"] = sensibilities

        # Extractions des évolutions 

        evolutions = []
        # On accède au tableau des évolutions
        evolution_table = response.xpath(
            '//table[.//th[contains(text(), "Famille d\'évolution")]]'
        )

        # On récupère les évolutions issu du pokemon dans la table
        for evolution_row in evolution_table.xpath(".//tr"):
            evolution_name_link = evolution_row.xpath(
                ".//td[last()]/a[@title][last()]/@title"
            ).get()
            if evolution_name_link:
                evolutions.append(evolution_name_link.strip())

        pokemon_item["evolutions"] = evolutions

        yield pokemon_item
