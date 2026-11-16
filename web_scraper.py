import csv
import hashlib
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


START_URL = "https://quotes.toscrape.com/"
OUTPUT_FILE = Path(__file__).with_name("scraped_quotes.csv")


def image_url_for_quote(quote, author):
    seed = hashlib.sha256(f"{quote}\0{author}".encode("utf-8")).hexdigest()[:16]
    return f"https://picsum.photos/seed/{seed}/800/450"


def scrape_quotes():
    quotes = []
    seen_quotes = set()
    visited_pages = set()
    page_url = START_URL

    while page_url:
        if page_url in visited_pages:
            raise RuntimeError(f"Pagination loop detected at {page_url}")
        visited_pages.add(page_url)

        response = requests.get(page_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        quote_cards = soup.select("div.quote")
        if not quote_cards:
            raise ValueError(f"No quote cards found on {page_url}")

        for card in quote_cards:
            quote_node = card.select_one("span.text")
            author_node = card.select_one("small.author")
            if quote_node is None or author_node is None:
                raise ValueError(f"A quote card is missing text or author on {page_url}")

            quote = quote_node.get_text(strip=True)
            author = author_node.get_text(strip=True)
            if (quote, author) not in seen_quotes:
                quotes.append(
                    {
                        "quote": quote,
                        "author": author,
                        "image_url": image_url_for_quote(quote, author),
                    }
                )
                seen_quotes.add((quote, author))

        next_link = soup.select_one("li.next a")
        page_url = urljoin(response.url, next_link["href"]) if next_link else ""
        if page_url:
            time.sleep(0.5)

    return quotes


def save_quotes(quotes, output_file=OUTPUT_FILE):
    if not quotes:
        raise ValueError("No quotes were collected; refusing to write an empty dataset.")

    with output_file.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=["quote", "author", "image_url"]
        )
        writer.writeheader()
        writer.writerows(quotes)


def display_quotes(quotes):
    from html import escape
    from IPython.display import HTML, Image, display

    for quote in quotes:
        text = escape(quote["quote"])
        author = escape(quote["author"])
        display(HTML(f"<p>{text}<br><strong>{author}</strong></p>"))

        image_url = quote.get("image_url", "").strip()
        if image_url:
            display(Image(url=image_url))


def main():
    quotes = scrape_quotes()
    save_quotes(quotes)
    print(f"Saved {len(quotes)} unique quotes to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
