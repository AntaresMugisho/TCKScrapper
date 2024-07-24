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
            {"name": "William Branham"},
            {"name": "Ewald Franck"},
            {"name": "Traités"},
            {"name": "Autres auteurs"},
        ],
    }

    author_index = 0
    books = []

    for table in all_tables:
        if table in author_tables:
            author_table = author_tables[author_index]
            author_name = data["authors"][author_index]["name"]
            author_index += 1

        elif table in brochure_tables:
            category = table.find("tr").text.replace("\n", "")
            if category == "Traités":
                start_index = 5
            else:
                start_index = 4

            rows = table.find_all("tr")[start_index:]


            for row in rows:
                tds = row.find_all("td")
                if author_name.startswith("William"):
                    books.append({
                        "title": tds[1].find("font").text.strip(),
                        "html": tds[2].find("a").get("href"),
                        "pdf": tds[3].find("a").get("href") if tds[3].find("a").text == "Imprimer" else "En cours",
                        "epub": tds[4].find("a").get("href") if tds[4].find("a").text == "Télécharger" else "En cours",
                        "category": category,
                        "author": author_name,
                    })
                else:
                    books.append({
                        "title": tds[0].find("font").text.strip(),
                        "html": tds[1].find("a").get("href"),
                        "pdf": tds[2].find("a").get("href") if tds[2].find("a").text == "Imprimer" else "En cours",
                        "epub": tds[3].find("a").get("href") if tds[3].find("a").text == "Télécharger" else "En cours",
                        "category": category,
                        "author": author_name,
                    })

    pprint(books)


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
