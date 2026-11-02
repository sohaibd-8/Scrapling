"""Iran-only drug price monitoring: validate provenance and compare snapshots.

Input CSV headers:
irc,drug_name,brand,manufacturer,form,strength,pack_size,price_rial,price_type,observed_at,source_url
Price is per explicitly specified pack, in IRR. Values must be verified against TTAC.
No automated TTAC access is attempted without an authorized integration.
"""
import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

FIELDS = ["irc", "drug_name", "brand", "manufacturer", "form", "strength",
          "pack_size", "price_rial", "price_type", "observed_at", "source_url"]
KEYS = ("irc", "pack_size", "price_type")
PRICE_TYPE = "official_consumer_price"


def validate_row(row):
    if any(not (row.get(k) or "").strip() for k in ("irc", "drug_name", "pack_size", "price_rial", "observed_at", "source_url")):
        raise ValueError("Required fields missing")
    if row.get("price_type") != PRICE_TYPE:
        raise ValueError("Only verified official consumer price is supported")
    parsed = urlparse(row["source_url"])
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("A public HTTPS source URL is required")
    try:
        value = Decimal(row["price_rial"])
        if value <= 0 or value != value.to_integral_value():
            raise ValueError("price_rial must be a positive whole number")
    except InvalidOperation as err:
        raise ValueError("Invalid price_rial") from err
    datetime.fromisoformat(row["observed_at"].replace("Z", "+00:00"))
    return row


def load(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise ValueError("Missing CSV headers")
        return [validate_row(row) for row in reader]


def compare(old, new):
    prior = {tuple(r[k] for k in KEYS): r for r in old}
    changes = []
    for row in new:
        key = tuple(row[k] for k in KEYS)
        if key in prior:
            prev = Decimal(prior[key]["price_rial"])
            current = Decimal(row["price_rial"])
            if prev != current:
                changes.append({
                    "irc": row["irc"], "drug_name": row["drug_name"],
                    "pack_size": row["pack_size"], "old_price_rial": str(prev),
                    "new_price_rial": str(current),
                    "change_percent": str(round((current - prev) * 100 / prev, 2)),
                    "source_url": row["source_url"],
                })
    return changes


def main():
    parser = argparse.ArgumentParser(description="Iran-only drug price snapshot monitor")
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output/iran_drug_changes.csv"))
    args = parser.parse_args()
    current = load(args.current)
    print(f"Validated {len(current)} Iranian drug-price records.")
    if args.previous:
        changes = compare(load(args.previous), current)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
            names = ["irc", "drug_name", "pack_size", "old_price_rial", "new_price_rial", "change_percent", "source_url"]
            writer = csv.DictWriter(handle, fieldnames=names)
            writer.writeheader()
            writer.writerows(changes)
        print(f"Price changes: {len(changes)}; exported to {args.output}")


if __name__ == "__main__":
    main()
