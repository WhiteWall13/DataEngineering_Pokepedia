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

        image_url = response.xpath(
            "//span[@typeof='mw:File']/a[@class='mw-file-description']/img/@src"
        ).get()
        if image_url:
            pokemon_item["image"] = response.urljoin(image_url)

        # stats = {}
        # for stat_row in response.xpath(
        #     "//table[contains(@class, 'tableau-overflow')]/tbody/tr"
        # ):
        #     stat_name = stat_row.xpath("td[1]/a/text()").get()
        #     stat_value = stat_row.xpath("td[2]/text()").get()

        #     if stat_name and stat_value:
        #         stat_value_cleaned = stat_value.strip()
        #         stats[stat_name.strip()] = stat_value_cleaned
        #         # if stat_value_cleaned.isdigit():
        #         #     stats[stat_name.strip()] = int(stat_value_cleaned)
        #         #     # print(
        #         #     #     f"Stats numériques pour {stat_name.strip()}: '{stat_value_cleaned} :)'"
        #         #     # )
        #         # else:
        #         #     print(
        #         #         f"Stats non numériques pour {stat_name.strip()}: {stat_value_cleaned} or {stat_value}"
        #         #     )
        # pokemon_item["stats"] = stats

        stats = {}
        # Sélectionner les tableaux qui contiennent "Statistiques indicatives" dans l'en-tête
        tables = response.xpath(
            "//th[contains(text(), 'Statistiques indicatives')]/ancestor::table"
        )

        for table in tables:
            for stat_row in table.xpath("./tbody/tr"):
                stat_name = stat_row.xpath("td[1]/a/text()").get()
                stat_value = stat_row.xpath("td[2]/text()").get()

                if stat_name and stat_value:
                    stats[stat_name.strip()] = int(stat_value.strip())

        pokemon_item["stats"] = stats

        evolutions = []
        evolution_table = response.xpath(
            '//table[.//th[contains(text(), "Famille d\'évolution")]]'
        )

        for evolution_row in evolution_table.xpath(".//tr"):
            evolution_name_link = evolution_row.xpath(
                ".//td[last()]/a[@title][last()]/@title"
            ).get()
            if evolution_name_link:
                evolutions.append(evolution_name_link.strip())

        pokemon_item["evolutions"] = evolutions

        # TODO : Bug évoli qui n'est pas dans les ses évolutions car case de gauche

        yield pokemon_item
