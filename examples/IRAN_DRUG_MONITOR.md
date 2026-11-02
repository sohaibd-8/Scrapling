# Iran Drug Price Monitor / پایش قیمت دارو در ایران

**Iran only.** This prototype never fetches US datasets or implies foreign prices apply to Iranian medicine. The authoritative consumer-price reference is **TTAC (https://www.ttac.ir/)**, according to Iran's Food and Drug Administration statements. An official public bulk price API and permission terms have **not been verified**, so this MVP intentionally does not scrape the TTAC site, bypass controls, or claim live price coverage.

## Workflow (MVP v0.1)

1. Obtain verifiable, authorized Iranian **product-level** price records through an approved workflow. Record the exact public source URL and collection timestamp. Do not enter unverified numbers.
2. Fill a UTF-8 CSV with these headers:
   `irc,drug_name,brand,manufacturer,form,strength,pack_size,price_rial,price_type,observed_at,source_url`
3. Use `price_type=official_consumer_price` **only if the record was checked against an official source**. `price_rial` is an integer amount **in Iranian rials (IRR)** for the specified pack; never silently convert to tomans.
4. Validate: `python examples/iran_drug_monitor.py --current /path/to/current.csv`
5. Compare like-for-like snapshots by IRC, pack size and price type:
   `python examples/iran_drug_monitor.py --previous /path/to/previous.csv --current /path/to/current.csv`

Output `output/iran_drug_changes.csv` reports old/new values and percentage changes. No records are populated by default because genuine Iranian price values have not yet been obtained. Validation alone **does not establish the truth of a submitted price**. Price records must be verified and approved before publication.

## Data policy

- Explicitly record IRC, brand, manufacturer, strength, form and pack size to avoid false comparisons between formulations or packages.
- Use timestamps in ISO-8601, with timezone.
- Keep provenance for every observation; distinguish prescribed/official consumer price from insurance copay, pharmacy payment, distributor/wholesale price and online retail listings.
- Never infer national availability or shortages from missing listings.
- No personally identifiable patient or prescription data.

## Access roadmap

1. Confirm a **documented, permitted** TTAC/IFDA bulk data access route or license.
2. Build a Scrapling adapter only for authorized public pages that allow automation; throttle requests and respect rate limits/terms. Prefer a formal API or official machine-readable export.
3. Add deduplication, persistence, scheduled runs and review-before-publishing dashboard.

References:
- https://www.ttac.ir/
- https://www.tasnimnews.ir/fa/news/1404/10/30/3497446/ (Iran FDA official pricing statement as reported)
