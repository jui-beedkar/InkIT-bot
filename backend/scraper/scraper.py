import requests
from bs4 import BeautifulSoup
import json
import re
import hashlib

BASE_URLS = [
    "https://www.inkitsolutions.com.au/",
    "https://www.inkitsolutions.com.au/services",
    "https://www.inkitsolutions.com.au/contact-us"
]

documents = []
seen_hashes = set()
page_id = 1


def clean_text(text):

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_noise(soup):

    tags_to_remove = [
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "form",
        "button",
        "svg"
    ]

    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()


def generate_hash(text):

    return hashlib.md5(text.encode()).hexdigest()


for url in BASE_URLS:

    print("Scraping:", url)

    response = requests.get(url)

    if response.status_code != 200:
        print("Skipped:", response.status_code)
        continue

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    remove_noise(soup)

    text_blocks = []

    for tag in soup.find_all([
        "h1",
        "h2",
        "h3",
        "p",
        "li"
    ]):

        text = clean_text(tag.get_text())

        if len(text) > 40:
            text_blocks.append(text)

    print("Blocks found:", len(text_blocks))

    for block in text_blocks:

        text_hash = generate_hash(block)

        if text_hash in seen_hashes:
            continue

        seen_hashes.add(text_hash)

        document = {

            "page_id": page_id,
            "title": block[:80],
            "content": block,
            "url": url,
            "category": url.split("/")[-1] or "home"

        }

        documents.append(document)

        page_id += 1


with open(
    "scraped_data.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        documents,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Scraping complete")
print("Total documents:", len(documents))