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


if __name__ == "__main__":
    with open("brochures.html", "r") as file:
        html = file.read()
        scrap_brochures(html)

    # url = "http://cmpp.ch//brochures.htm"
    # url2 = "http://cmpp.ch//lettre_circulaire.htm"
    #
    # try:
    #     response = requests.get(url)
    #     html = response.text
    #     with open("brochures.html", "w") as file:
    #         file.write(html)
    # except requests.RequestException as e:
    #     print(f"Error: {e}")
    #
    # else:
    #     with open("brochures.html", "r") as file:
    #         html = file.read()
    #         scrap(html)
