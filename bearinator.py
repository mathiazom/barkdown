import requests
from bs4 import BeautifulSoup
import re
from colorama import init
from termcolor import colored

BOOK_URL_SOURCE_FILE = "booklist.txt"
BOOK_DATA_SOURCE_PREFIX = "https://www.adlibris.com/no/bok/"
MARKDOWN_FILE = "booklist.md"

def update_markdown(filename, markdown):

    print("Updating markdown... ",end="")

    file = open(filename,"w")
    file.write(markdown)
    file.close()

    print(colored("Done","green"))

def read_data_lines(filename):

    f = open(filename,"r")
    data = f.readlines()
    f.close()
    return data

def generate_markdown(books):

    print("Generating markdown... ",end="")

    markdown = """>Liste over bøker jeg ønsker å fylle bokhylla med, der interesse-tyngdepunktet ligger i toppen.\n>\n><cite>- Mathias</cite>\n\n"""

    markdown += generate_markdown_from_book(books.pop(0),1)

    for i,book in enumerate(books):
        markdown += "---\n"
        markdown += generate_markdown_from_book(book, i+2)

    print(colored("Done","green"))

    return markdown

# book = (title, author, adlibris_url, image_url, description)
def generate_markdown_from_book(book, i):

    description = book[4] if (len(book[4]) <= 500) else (book[4][:500] + " ...")

    return f"![{book[0]}]({book[3]})\n" + \
        f"## {i}. {book[0]}\n" + \
        f"{book[1]}\n\n" + \
        f"[{book[2]}]({book[2]})\n" + \
        f">{description}\n"


def get_book_from_url(url):

    page = BeautifulSoup(requests.get(url).text, 'html.parser')

    scripts = page.findAll("script")

    title = page.find('meta',{'property':'og:title'}).attrs['content']
    img_url = page.find('meta',{'property':'og:image:secure_url'}).attrs['content']
    url = page.find('meta',{'property':'og:url'}).attrs['content']
    description = page.find('meta',{'property':'og:description'}).attrs['content']

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

    print(title)

    return (title,author,url,img_url,description)


def get_book_urls():

    print("Retrieving URLs from file... ",end="")

    suffixes = read_data_lines(BOOK_URL_SOURCE_FILE)

    print(colored(f"Found {len(suffixes)} URLs","green"))

    return [BOOK_DATA_SOURCE_PREFIX + s.strip() for s in suffixes]


def main():

    init()

    # Get URLs from file
    urls = get_book_urls()

    # Get adlibris data from URL
    books = [get_book_from_url(url) for url in urls]

    # Generate markdown
    markdown = generate_markdown(books)

    # Write to markdown file
    update_markdown(MARKDOWN_FILE, markdown)


main()
