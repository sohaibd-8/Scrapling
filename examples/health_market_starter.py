"""Small, permission-conscious Scrapling demo using a public practice website.

Run after installing Scrapling:
    pip install scrapling
    python examples/health_market_starter.py

This is an extraction-pipeline smoke test, not a medical-data collector.
"""
import csv
from pathlib import Path

from scrapling.fetchers import Fetcher

URL = "https://quotes.toscrape.com/"
OUTPUT = Path("output/scrapling_demo.csv")


def main() -> None:
    page = Fetcher.get(URL)
    rows = []
    for item in page.css(".quote"):
        quote = item.css(".text::text").get()
        author = item.css(".author::text").get()
        if quote and author:
            rows.append({"quote": quote.strip(), "author": author.strip(), "source_url": URL})

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["quote", "author", "source_url"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
