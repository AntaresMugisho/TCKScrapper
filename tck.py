import requests
from bs4 import BeautifulSoup

soup = BeautifulSoup()

def scrap(html):
    print("Hello")


if __name__ == "__main__":
    url = "http://cmpp.ch//brochures.htm"

    response = requests.get(url)
    print(response.text)

    # Parole parlée, brochures, livres, ...

    # author = table > tr[0] > td > font.text if len(tr) == 1

    # category = tab > tr[1] > td > font.text
    # tds [] = tab > tr[4] or tr[5] for if category == "Traités"

    # title =  tds[2] > font.text
    # html_content = tds[3] > div > font > a.href
    # pdf_file = tds[4] > div > font > a if a.text == "Imprimer"


    # Autres ...

    # Lettres circulaires => "http://cmpp.ch//lettre_circulaire.htm"
            # - Date, Contenu, Lien htm, Lien PDF
    # Somaire