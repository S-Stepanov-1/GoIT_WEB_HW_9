import json

from models import Authors, Quotes
from connect import create_connect


def get_data(file_path: str) -> list[dict]:
    with open(file_path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    return data


def fill_authors(authors: list[dict]) -> None:

    for author in authors:

        is_existing_author = Authors.objects(fullname=author["fullname"])
        if is_existing_author:
            continue

        else:
            new_author = Authors(fullname=author["fullname"],
                                 born_date=author["born_date"],
                                 born_location=author["born_location"],
                                 description=author["description"])
            new_author.save(validate=False)


def fill_quotes(quotes: list[dict]) -> None:

    for quote in quotes:
        try:
            author_obj_id = Authors.objects.get(fullname=quote["author"]).id
            new_quote = Quotes(tags=quote["tags"],
                               author=author_obj_id,
                               quote=quote["quote"])
            new_quote.save(validate=False)

        except Exception :
            new_quote = Quotes(tags=quote["tags"],
                               author=quote["author"],
                               quote=quote["quote"])
            new_quote.save(validate=False)


if __name__ == '__main__':
    create_connect()  # connection to DB

    authors = get_data("authors.json")  # authors as a list of dictionaries
    quotes = get_data("quotes.json")  # quotes as a list of dictionaries

    print("Writing to DB...")
    fill_authors(authors)
    fill_quotes(quotes)
