import json

import requests
from bs4 import BeautifulSoup

URL_main = "https://quotes.toscrape.com"
URL_login = "https://quotes.toscrape.com/login"
URL_author = "https://www.goodreads.com"

LOGIN_DATA = {"username": "admin", "password": "admin"}


def do_login(url: str, session):
    response = session.post(url, data=LOGIN_DATA)
    if response.status_code == 200:
        return True
    else:
        print(f"\nSomething went wrong...\n[X] Status code: {response.status_code}")
        return False


def get_html_soup(url: str, session):
    response = session.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "lxml")
    else:
        print(f"\nSomething went wrong...\n[X] Status code: {response.status_code}")


def get_full_author_info(urls: tuple, session) -> dict:
    author_soup = get_html_soup(urls[0], session)

    fullname = author_soup.find("h3", class_="author-title").text.strip()
    born_date = author_soup.find("span", class_="author-born-date").text.strip()
    location = author_soup.find("span", class_="author-born-location").text.strip()
    description = author_soup.find("div", class_="author-description").text.strip()

    link_with_photo = urls[1]
    photo_soup = get_html_soup(link_with_photo, session)
    photo_link = photo_soup.find("img", itemprop="image")["src"]

    authors_data = {"fullname": fullname,
                    "born_date": born_date,
                    "born_location": location,
                    "description": description,
                    "photo": photo_link}

    return authors_data


def get_quote_info(card: BeautifulSoup) -> dict:
    quote = card.find_next("span", class_="text").text.strip()
    tags = card.find_next("div", class_="tags").findChildren("a", class_="tag")
    author = card.find_next("small", class_="author").text.strip()

    quote_data = {"tags": [tag.text.strip() for tag in tags],
                  "author": author,
                  "quote": quote}

    return quote_data


# creating json files, open them for writing and save info
def create_json_files(authors_data, quotes_data):
    with open("authors.json", "w", encoding="utf-8") as authors_json:
        json.dump(authors_data, authors_json, indent=4, ensure_ascii=False)

    with open("quotes.json", "w", encoding="utf-8") as quotes_json:
        json.dump(quotes_data, quotes_json, indent=4, ensure_ascii=False)


def main():
    quotes_data = []
    authors_data = []

    authors_link = set()

    stop_parser = False
    page_num = 1  # page's number on the website

    session = requests.Session()

    if do_login(URL_login, session):
        print(f"Web scraper is running...")

        while not stop_parser:
            page_soup = get_html_soup(URL_main + f"/page/{page_num}", session)

            # if there are no more quotes on the page we will see "No quotes found!" it means we should stop the scraper
            # ----------------------------------------------------------------------
            signal_element = page_soup.select("div.col-md-8")[1].text.split("←")
            if signal_element[0].strip() == "No quotes found!":
                stop_parser = True
                continue

            # ----------------------------------------------------------------------

            # ======================== Handle soup ==========================================
            cards = page_soup.find_all("div", class_="quote")  # all cards on the page
            for card in cards:
                author_page = card.find_next("a").get("href")  # all info about author
                extra_author_page = card.find_next("span").find_next("span").find_next("a").find_next("a").get("href")  # author's photo

                authors_link.add((URL_main + author_page, extra_author_page))

                quotes_data.append(get_quote_info(card))  # extract info about quote and add it to the quotes_data list

            page_num += 1

        # extract info about author and add it to the authors_data list
        for author_link in authors_link:
            authors_data.append(get_full_author_info(author_link, session))

            # ===================================================================================

        create_json_files(authors_data, quotes_data)


if __name__ == '__main__':
    main()
