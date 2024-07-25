import datetime
import json
import os.path
import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup, ResultSet

BASE_URL = "http://www.cmpp.ch/"

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
        "last_update": datetime.datetime.utcnow().isoformat(),
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
                        "id": len(books) + 1,
                        "author_id": author_id,
                        "category_id": category.get("id"),
                        "title": title,
                        "html": html,
                        "pdf": pdf,
                        "epub": epub,
                    })

    data["categories"] = categories
    data["books"] = books

    with open("brochures.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def scrap_letters(html):
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")

    # The table containing letters is the second
    table = tables[1]
    rows = table.find_all("tr")[3:]

    data = {
        "last_update": datetime.datetime.utcnow().isoformat(),
        "letters": []
    }

    letters = []

    i = 0
    for row in rows:
        tds = row.find_all("td")

        date = " ".join(tds[1].text.split())
        text = tds[2].find("font").text.replace("\x97", "|")
        text = " ".join(text.split())
        contents = [t.strip() for t in text.split("|")[1:]]

        letter = {
            "id": len(letters) + 1,
            "date": date,
            "contents": contents,
            "html": tds[3].find("a").get("href").replace(BASE_URL, ""),
            "pdf": tds[4].find("a").get("href").replace(BASE_URL, ""),
            "epub": tds[5].find("a").get("href").replace(BASE_URL, ""),

        }
        letters.append(letter)

    data["letters"] = letters

    with open("letters.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def scrap():
    brochures_url = "http://cmpp.ch//brochures.htm"
    letters_url = "http://cmpp.ch//lettre_circulaire.htm"

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


def get_books():
    with open("brochures.json", "r") as file:
        data = json.load(file)
    return data.get("books")

def extract_images(html):
    soup = BeautifulSoup(html, "html.parser")
    imgs = soup.find_all("img")
    images = [img.get("src") for img in imgs]
    return images


def get_letters():
    with open("letters.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("letters")


def download(filename: str, dir: str):
    with requests.get(f"{BASE_URL}{filename}", stream=True) as response:
        response.raise_for_status()
        with open(os.path.join(dir, filename), "wb") as file:
            for chunk in response.iter_content(8192):
                file.write(chunk)


def save_html(filename, dir):
    response = requests.get(f"{BASE_URL}{filename}")
    response.raise_for_status()

    filename = f"{os.path.splitext(filename)[0]}.html"
    with open(os.path.join(dir, filename), "w", encoding="utf-8") as file:
        # Save html file
        file.write(response.text)

        # Save images in html
        for img in extract_images(response.text):
            download(img, dir)


def download_letters():
    letters = get_letters()
    # for letter in letters:
    #     print(f"Downloading letter pdf #{letter.get('id')} of {len(letters)}")
    #     download(letter.get("pdf"), "letters/pdf")
    #
    # for letter in letters:
    #     print(f"Downloading letter epub #{letter.get('id')} of {len(letters)}")
    #     download(letter.get("epub"), "letters/epub")

    for letter in letters:
        print(f"Downloading letter html #{letter.get('id')} of {len(letters)}")
        save_html(letter.get("html"), "letters/html")


def download_books():
    books = get_books()
    for book in books:
        if book.get("pdf"):
            print(f"Downloading pdf book #{book.get('id')} of {len(books)}")
            download(book.get("pdf"), "brochures/pdf")

    for book in books:
        if book.get("epub"):
            print(f"Downloading epub book #{book.get('id')} of {len(books)}")
            download(book.get("epub"), "brochures/epub")

    for book in books:
        print(f"Downloading html book #{book.get('id')} of {len(books)}")
        save_html(book.get("html"), "brochures/html")


if __name__ == "__main__":
    # scrap()
    download_letters()
    # download_books()



