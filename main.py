import datetime
import json
from pprint import pprint

import requests
from bs4 import BeautifulSoup


def scrap_brochures(html: str):
    soup = BeautifulSoup(html, "html.parser")

    all_tables = soup.find_all("table")

    author_tables = []
    brochure_tables = []
    for table in all_tables:
        # Tables containing author's name has just 1 tr inside
        if len(table.find_all("tr")) == 1:
            author_tables.append(table)
        else:
            brochure_tables.append(table)

    # Remove the last table as it's not an author table but a table used for copyright
    author_tables.pop()

    #Remove the last table as it not contains books
    brochure_tables.pop()

    data = {
        "last_update": datetime.datetime.utcnow(),
        "authors": [
            {"id": 1,
             "name": "William Branham"
             },
            {"id": 2,
             "name": "Ewald Franck"
             },
            {"id": 3,
             "name": "Traités"
             },
            {"id": 4,
             "name": "Autres auteurs"
             },
        ],
        "categories": [],
        "books": [],
    }

    categories = []
    books = []

    for table in all_tables:
        if table in author_tables:
            author_id = data["authors"][author_tables.index(table)].get("id")

        elif table in brochure_tables:
            category_name = ' '.join(table.find("tr").text.split())
            category = {
                "id": len(categories) + 1,
                "name": category_name,
            }

            if category.get("name") in [c.get("name") for c in categories]:
                for c in categories:
                    if c.get("name") == category.get("name"):
                        category = c
            else:
                categories.append(category)

            if category.get("name") == "Traités":
                row_start_index = 4
            else:
                row_start_index = 3
            if category.get("name") == "Hors série…" or author_id != 1:
                col_start_index = 0
            else:
                col_start_index = 1

            rows = table.find_all("tr")[row_start_index:]

            for row in rows:
                tds = row.find_all("td")
                if len(tds) > 2:
                    title = " ".join(tds[col_start_index].find("p").text.split())
                    html = tds[col_start_index+1].find("a").get("href")
                    try:
                        pdf = tds[col_start_index+2].find("a").get("href")
                        if category.get("name") != "Traités":
                            epub = tds[col_start_index+3].find("a").get("href")
                        else:
                            epub = tds[col_start_index+4].find("a").get("href")
                    except (AttributeError, IndexError):
                        pdf = epub = False

                    books.append({
                        "author_id": author_id,
                        "category_id": category.get("id"),
                        "title": title,
                        "html": html,
                        "pdf": pdf,
                        "epub": epub,
                    })

    data["categories"] = categories
    data["books"] = books

    with open("brochures.json", "w", encoding="utf8") as file:
        json.dump(data, file, indent=4)


def scrap_letters(html):
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")

    # The table containing letters is the second
    table = tables[1]
    rows = table.find_all("tr")[3:]

    data = {
        "last_update": datetime.datetime.utcnow(),
        "letters": []
    }

    letters = []

    for row in rows:
        tds = row.find_all("td")
        letter = {
            "id": len(letters) + 1,
            "date": tds[1].text.strip(),
            "content":tds[2].text.strip(),
            "html": tds[3].find("a").get("href"),
            "pdf": tds[4].find("a").get("href"),
            "epub": tds[5].find("a").get("href"),

        }
        letters.append(letter)
    data["letters"] = letters

    with open("letters", "w", encoding="utf8") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    brochures_url = "http://localhost:63342/TckScrapper/brochures.htm"
    letters_url = "http://localhost:63342/TckScrapper/lettre_circulaire.htm"

    try:
        brochures = requests.get(brochures_url)
        letters = requests.get(letters_url)
        brochures.raise_for_status()
        letters.raise_for_status()
    except requests.RequestException as e:
        print(f"[Error] {e}")
    else:
        br = brochures.text
        lt = letters.text
        scrap_brochures(br)
        scrap_letters(lt)

