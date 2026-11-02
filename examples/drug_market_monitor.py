"""Drug market monitor: FDA product metadata + official NADAC CSV ingestion.

No clinical use. NADAC is US pharmacy acquisition cost, NOT retail price.
Run:
    python examples/drug_market_monitor.py --drug ibuprofen
    python examples/drug_market_monitor.py --drug ibuprofen --nadac-csv path/to/nadac.csv
The optional CSV must be downloaded from https://data.medicaid.gov/dataset/fbb83258-11c7-47f5-8b18-5f8e79f7e704
"""
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

FDA_ENDPOINT = "https://api.fda.gov/drug/ndc.json"
NADAC_SOURCE = "https://data.medicaid.gov/dataset/fbb83258-11c7-47f5-8b18-5f8e79f7e704"
COLUMNS = ["ndc", "drug_name", "brand_name", "manufacturer", "dosage_form", "strength",
           "price_value", "price_unit", "currency", "price_type", "price_date",
           "data_source", "source_url", "collected_at"]


def fetch_fda(drug: str, limit: int = 10) -> list[dict]:
    query = urlencode({"search": f'generic_name:"{drug}"', "limit": limit})
    req = Request(FDA_ENDPOINT + "?" + query, headers={"User-Agent": "DrugMarketMonitor/0.1 (research)"})
    with urlopen(req, timeout=25) as response:
        payload = json.load(response)
    collected = datetime.now(timezone.utc).isoformat()
    rows = []
    for item in payload.get("results", []):
        rows.append(dict(
            ndc=item.get("product_ndc", ""), drug_name=item.get("generic_name", ""),
            brand_name=item.get("brand_name", ""), manufacturer=item.get("labeler_name", ""),
            dosage_form=item.get("dosage_form", ""), strength="; ".join(
                x.get("strength", "") for x in item.get("active_ingredients", []) if isinstance(x, dict)),
            price_value="", price_unit="", currency="", price_type="",
            price_date="", data_source="openFDA_NDC", source_url=FDA_ENDPOINT,
            collected_at=collected))
    return rows


def read_nadac_csv(path: Path, drug: str, max_matches: int = 100) -> list[dict]:
    """Read a downloaded official CSV; do not infer package prices or blend NDC formats."""
    collected = datetime.now(timezone.utc).isoformat()
    found = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"NDC Description", "NDC", "NADAC Per Unit", "Pricing Unit", "Effective Date"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Unsupported NADAC CSV schema: required columns absent")
        for item in reader:
            if drug.casefold() not in item["NDC Description"].casefold():
                continue
            found.append(dict(
                ndc=item["NDC"], drug_name=item["NDC Description"], brand_name="",
                manufacturer="", dosage_form="", strength="",
                price_value=item["NADAC Per Unit"], price_unit=item["Pricing Unit"],
                currency="USD", price_type="US_NADAC_PHARMACY_ACQUISITION_PER_UNIT",
                price_date=item["Effective Date"], data_source="CMS_NADAC",
                source_url=NADAC_SOURCE, collected_at=collected))
            if len(found) >= max_matches:
                break
    return found


def export_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Drug product metadata and NADAC research export")
    parser.add_argument("--drug", required=True, help="Generic drug name in English")
    parser.add_argument("--nadac-csv", type=Path, help="Official local NADAC CSV download (optional)")
    parser.add_argument("--offline", action="store_true", help="Skip FDA network call")
    parser.add_argument("--output-dir", type=Path, default=Path("output/drug_market"))
    args = parser.parse_args()
    if not args.drug.strip() or any(ch in args.drug for ch in '\r\n"'):
        parser.error("Drug must be a nonempty single-line name without double quotes")
    rows = []
    if not args.offline:
        try:
            rows = fetch_fda(args.drug)
        except Exception as exc:
            print(f"FDA query failed: {exc}. No FDA records exported.")
    export_csv(rows, args.output_dir / "products.csv")
    print(f"FDA products: {len(rows)}")
    if args.nadac_csv:
        prices = read_nadac_csv(args.nadac_csv, args.drug)
        export_csv(prices, args.output_dir / "nadac_costs.csv")
        print(f"NADAC cost observations: {len(prices)}")
    print("NADAC is NOT retail price. FDA NDC and NADAC package identifiers are not automatically joined.")


if __name__ == "__main__":
    main()
