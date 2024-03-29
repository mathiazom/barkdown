import datetime
from os import environ

import requests
import re
from bs4 import BeautifulSoup
from colorama import init
from dotenv import load_dotenv
from termcolor import colored

load_dotenv()

'''
    Bear page acting as source for book URLs
'''
BOOK_URL_SOURCE = environ["BOOK_URL_SOURCE"]

'''
    Adlibris website prefix
'''
BOOK_DATA_SOURCE_PREFIX = environ["BOOK_DATA_SOURCE_PREFIX"]


def get_book_urls():
    """
        Retrieve list of book urls from the defined Bear page
    """
    print(f"Retrieving book URLs from {BOOK_URL_SOURCE}")

    page = BeautifulSoup(requests.get(BOOK_URL_SOURCE).text, 'html.parser')

    books = page.find("div", {'id': 'books'})

    suffixes = books.findAll("p")

    print(colored(f"Found {len(suffixes)} book URLs", "green"))

    return [BOOK_DATA_SOURCE_PREFIX + s.string.strip() for s in suffixes]


def get_book_author_from_page(page):
    """
        Extract the author of the book presented on the given page
        Author field is less accessible than the title and description,
        but can be retrieved from an inline Javascript variable
    """
    scripts = page.findAll("script")

    author = ""
    for s in scripts:

        if not s.contents:
            continue

        content = s.contents[0]

        author_match = re.search('"Authors":\[".*"\]', content)

        if not author_match:
            continue

        author_string = author_match.group()

        author = re.search('\[".*"\]', author_string).group()[2:-2]

    return author


def clean_book_html_data(html):
    return BeautifulSoup(html, "lxml").text.replace("\n", "")


def get_book_from_url(url):
    """
        Extract data about the book from the page on the given url
        returns book as tuple
    """
    page = BeautifulSoup(requests.get(url).text, 'html.parser')

    return {
        "title": clean_book_html_data(page.find('meta', {'property': 'og:title'}).attrs['content']),
        "author": clean_book_html_data(get_book_author_from_page(page)),
        "img_url": page.find('meta', {'property': 'og:image:secure_url'}).attrs['content'],
        "url": page.find('meta', {'property': 'og:url'}).attrs['content'],
        "description": page.find('meta', {'property': 'og:description'}).attrs['content']
    }


def generate_markdown_from_book(book, i):
    """
        Generate markdown representing the given book, and the given list position
    """
    desc = book['description']
    description = (desc if (len(desc) <= 500) else (desc[:500] + " ...")).replace("\n", "  \n>")

    return f"![{book['title']}]({book['img_url']})\n" + \
           f"## {i}. {book['title']}\n" + \
           f"{book['author']}\n\n" + \
           f"[{book['url']}]({book['url']})\n" + \
           f">{description}\n"


def generate_markdown_from_books(books):
    """
        Generate main markdown body to represent the given list of books
    """
    print("Generating markdown... ", end="")

    markdown = f"*Oppdatert {datetime.datetime.now().date().isoformat()}*"

    markdown += """\n\n>Liste over bøker jeg ønsker å fylle bokhylla med, der interesse-tyngdepunktet ligger i toppen.\n\n """

    for i, book in enumerate(books):
        book_markdown = ("---\n" if i > 0 else "") + generate_markdown_from_book(book, i + 1)
        markdown += book_markdown

    print(colored("Done", "green"))

    return markdown


def generate_markdown():
    """
        - Retrieve book URLs from defined Bear page
        - Extract book data from URLs
        - Generate markdown source from data
    """
    # Terminal colors
    init()

    # Retrieve book urls
    urls = get_book_urls()

    # Get Adlibris data from URLs
    books = [get_book_from_url(url) for url in urls]

    return generate_markdown_from_books(books)
