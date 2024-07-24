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

    pprint(len(brochure_tables))

    data = {
        "authors": [
            {"name": "William Branham"},
            {"name": "Ewald Franck"},
            {"name": "Autres auteurs"},
        ],
    }

    for table in all_tables:
        if table in author_tables:
            author = author_tables[0]

        # category = tab > tr[1] > td > font.text
        # tds [] = tab > tr[4] or tr[5] if category == "Traités"

        # title =  tds[2] > font.text
        # html_content = tds[3] > div > font > a.href
        # pdf_file = tds[4] > div > font > a if a.text == "Imprimer"

        # Autres ...

        # Lettres circulaires => "http://cmpp.ch//lettre_circulaire.htm"
        # - Date, Contenu, Lien htm, Lien PDF
        # Somaire


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
