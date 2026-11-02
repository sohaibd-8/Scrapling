"""Iranian public medicine page inspector using Scrapling.

Single-page, low-volume exploratory extraction; NOT an official price feed.
python examples/iran_public_medicine_reader.py --url https://www.pillix.ir/medicine
"""
import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

FIELDS = ["label", "detail_url", "source", "retrieved_utc", "price_status"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="https://www.pillix.ir/medicine")
    p.add_argument("--output", type=Path, default=Path("output/iran_medicine_catalog.csv"))
    args = p.parse_args()
    parts = urlparse(args.url)
    if parts.scheme != "https" or parts.hostname not in ("pillix.ir", "www.pillix.ir"):
        p.error("Only public Pillix HTTPS pages allowed in this exploratory adapter")
    from scrapling.fetchers import Fetcher
    page = Fetcher.get(args.url)
    if getattr(page, "status", 200) != 200:
        raise RuntimeError("Site did not return HTTP 200; aborting")
    retrieved = datetime.now(timezone.utc).isoformat()
    records = []
    for link in page.css("a[href]"):
        label = (link.css("::text").get() or "").strip()
        href = link.attrib.get("href", "")
        if not label or not href or "mg" not in label.lower():
            continue
        from urllib.parse import urljoin
        target = urljoin(args.url, href)
        if urlparse(target).hostname not in ("pillix.ir", "www.pillix.ir"):
            continue
        records.append({"label": label, "detail_url": target, "source": args.url,
                        "retrieved_utc": retrieved, "price_status": "NOT_COLLECTED"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    print(f"Collected {len(records)} candidate catalog links, not official prices")

if __name__ == "__main__":
    main()
