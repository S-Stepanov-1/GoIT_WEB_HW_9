import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL_main = "https://quotes.toscrape.com"
ua = UserAgent(browsers=["chrome", "opera", "firefox"])


def get_html_soup(url: str):
    headers = {"User-Agent": ua.random}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "lxml")
    else:
        print(f"\nSomething went wrong...\n[X] Status code: {response.status_code}")


def get_full_author_info(url: str) -> dict:
    author_soup = get_html_soup(url)

    fullname = author_soup.find("h3", class_="author-title").text.strip()
    born_date = author_soup.find("span", class_="author-born-date").text.strip()
    location = author_soup.find("span", class_="author-born-location").text.strip()
    description = author_soup.find("div", class_="author-description").text.strip()

    authors_data = {"fullname": fullname,
                    "born_date": born_date,
                    "born_location": location,
                    "description": description}

    return authors_data


def get_quote_info(card: BeautifulSoup) -> dict:
    quote = card.find_next("span", class_="text").text.strip()
    tags = card.find_next("div", class_="tags").findChildren("a", class_="tag")
    author = card.find_next("small", class_="author").text.strip()

    quote_data = {"tags": [tag.text.strip() for tag in tags],
                  "author": author,
                  "quote": quote}

    return quote_data


def main():
    stop_parser = False
    page_num = 1  # page number on the website

    authors_data = []
    quotes_data = []

    while not stop_parser:
        soup = get_html_soup(URL_main + f"/page/{page_num}")

        # if there are no more quotes on the page we will see "No quotes found!", it means we should stop the scraper
        signal_element = soup.select("div.col-md-8")[1].text.split("←")
        if signal_element[0].strip() == "No quotes found!":
            stop_parser = True
            continue

        print(f"Page {page_num} in processing...")
        # --------------=== Handle soup ===------------------------------------
        cards = soup.find_all("div", class_="quote")  # all cards on the page
        for card in cards:
            quotes_data.append(get_quote_info(card))  # extract info about quote and add it to the quotes_data list

            # extract info about author and add it to the authors_data list
            author_page = card.find_next("a").get("href")
            authors_data.append(get_full_author_info(URL_main + author_page))
        # -----------------------------------------------------------------------
        page_num += 1

    # creating json files, open them for writing and save info
    with open("authors.json", "w", encoding="utf-8") as authors_json:
        json.dump(authors_data, authors_json, indent=4, ensure_ascii=False)

    with open("quotes.json", "w", encoding="utf-8") as quotes_json:
        json.dump(quotes_data, quotes_json, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
