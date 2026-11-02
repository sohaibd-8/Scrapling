"""Inspect a public TTAC web page with Scrapling (no API or access bypass).

Run from repository root:
 python examples/ttac_public_reader.py --url https://www.ttac.ir/ --mode http
 python examples/ttac_public_reader.py --url <PUBLIC_TTAC_RESULT_URL> --mode browser \
   --row-selector '<verified row CSS>' --name-selector '<verified name CSS>' \
   --price-selector '<verified price CSS>'

Selector arguments must be determined from an actual accessible public result page.
The output is observational/unverified until cross-checked against TTAC's public UI.
"""
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
COLUMNS = ["drug_name_raw", "price_raw", "price_digits_unverified",
           "source_url", "observed_at_utc", "verification_status"]


def verify_url(url):
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or (host != "ttac.ir" and not host.endswith(".ttac.ir")):
        raise ValueError("Only public HTTPS ttac.ir pages are supported")
    if parsed.username or parsed.password or parsed.port:
        raise ValueError("Credentials and custom ports are not supported")
    return url


def parse_price_digits(text):
    """Normalize characters, NOT currency or packaging unit."""
    s = (text or "").translate(PERSIAN_DIGITS)
    s = re.sub(r"[,،\s]", "", s)
    m = re.search(r"\d+", s)
    return m.group(0) if m else ""


def fetch(url, mode):
    from scrapling.fetchers import Fetcher, StealthyFetcher
    if mode == "http":
        return Fetcher.get(url)
    # Ordinary browser rendering only: no CAPTCHA solving or stealth bypass settings.
    return StealthyFetcher.fetch(url, headless=True, solve_cloudflare=False)


def extract(page, row_selector, name_selector, price_selector, url):
    timestamp = datetime.now(timezone.utc).isoformat()
    rows = []
    for item in page.css(row_selector):
        name = item.css(name_selector).get()
        price = item.css(price_selector).get()
        if name or price:
            rows.append({
                "drug_name_raw": name or "", "price_raw": price or "",
                "price_digits_unverified": parse_price_digits(price),
                "source_url": url, "observed_at_utc": timestamp,
                "verification_status": "UNVERIFIED_PUBLIC_PAGE_EXTRACTION",
            })
    return rows


def main():
    p = argparse.ArgumentParser(description="Public TTAC page inspector using Scrapling")
    p.add_argument("--url", required=True)
    p.add_argument("--mode", choices=("http", "browser"), default="http")
    p.add_argument("--row-selector")
    p.add_argument("--name-selector")
    p.add_argument("--price-selector")
    p.add_argument("--output-dir", type=Path, default=Path("output/ttac_inspection"))
    args = p.parse_args()
    url = verify_url(args.url)
    selectors = [args.row_selector, args.name_selector, args.price_selector]
    if any(selectors) and not all(selectors):
        p.error("Provide all three selectors together")
    page = fetch(url, args.mode)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # No raw page dump: pages may contain user-specific details.
    summary = {
        "url": url, "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "page_title": page.css("title::text").get() or "",
        "headings": page.css("h1::text").getall()[:10],
        "public_links_found": len(page.css("a[href]")),
        "selectors_configured": bool(all(selectors)),
    }
    (args.output_dir / "inspection.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if all(selectors):
        rows = extract(page, *selectors, url)
        with (args.output_dir / "unverified_rows.csv").open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Extracted {len(rows)} unverified rows. Confirm currency, package and official price manually.")


if __name__ == "__main__":
    main()
