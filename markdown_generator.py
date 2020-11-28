import requests
import re
from bs4 import BeautifulSoup
from colorama import init
from termcolor import colored

'''
    Bear page acting as source for book URLs
'''
BOOK_URL_SOURCE = "https://foxtrot.bearblog.dev/bearbookslist/"

'''
    Adlibris website prefix
'''
BOOK_DATA_SOURCE_PREFIX = "https://www.adlibris.com/no/bok/"


'''
    Retrieve list of book urls from the defined Bear page
'''
def get_book_urls():

    print(f"Retrieving URLs from {BOOK_URL_SOURCE}")

    page = BeautifulSoup(requests.get(BOOK_URL_SOURCE).text, 'html.parser')

    list = page.find("div",{'id':'books'})

    suffixes = list.findAll("p")

    print(colored(f"Found {len(suffixes)} URLs","green"))

    return [BOOK_DATA_SOURCE_PREFIX + s.string.strip() for s in suffixes]


'''
    Extract the author of the book presented on the given page
    Author field is less accessable than the title and description,
    but can be retrieved from an inline Javascript variable
'''
def get_book_author_from_page(page):

    scripts = page.findAll("script")

    author = ""
    for s in scripts:

        if not s.contents:
            continue

        content = s.contents[0]

        authorMatch = re.search('"Authors":\[".*"\]',content)

        if not authorMatch:
            continue

        author_string = authorMatch.group()

        author = re.search('\[".*"\]',author_string).group()[2:-2]

    return author

'''
    Extract data about the book from the page on the given url
    returns book as tuple
'''
def get_book_from_url(url):

    page = BeautifulSoup(requests.get(url).text, 'html.parser')

    title = page.find('meta',{'property':'og:title'}).attrs['content']
    author = get_book_author_from_page(page)
    img_url = page.find('meta',{'property':'og:image:secure_url'}).attrs['content']
    url = page.find('meta',{'property':'og:url'}).attrs['content']
    description = page.find('meta',{'property':'og:description'}).attrs['content']

    return (title,author,url,img_url,description)

'''
    Generate markdown representing the given book, and the given list position
'''
def generate_markdown_from_book(book, i):

    description = book[4] if (len(book[4]) <= 500) else (book[4][:500] + " ...")

    return f"![{book[0]}]({book[3]})\n" + \
        f"## {i}. {book[0]}\n" + \
        f"{book[1]}\n\n" + \
        f"[{book[2]}]({book[2]})\n" + \
        f">{description}\n"

'''
    Generate main markdown body to reprensent the given list of books
'''
def generate_markdown_from_books(books):

    print("Generating markdown... ",end="")

    markdown = """>Liste over bøker jeg ønsker å fylle bokhylla med, der interesse-tyngdepunktet ligger i toppen.\n>\n><cite>- Mathias</cite>\n\n"""

    markdown += generate_markdown_from_book(books.pop(0),1)

    for i,book in enumerate(books):
        book_markdown = "---\n" + generate_markdown_from_book(book, i+2)
        markdown += book_markdown

    print(colored("Done","green"))

    return markdown

'''
    - Retrieve book URLs from defined Bear page
    - Extract book data from URLs
    - Generate markdown source from data
'''
def generate_markdown():

    # Terminal colors
    init()

    # Retrieve book urls
    urls = get_book_urls()

    # Get adlibris data from URLs
    books = [get_book_from_url(url) for url in urls]

    return generate_markdown_from_books(books)
