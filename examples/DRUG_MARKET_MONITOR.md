# Drug Market Monitor — MVP 0.1

Research-only proof of concept for **public drug product metadata** and **US pharmacy acquisition cost**. It is **not** a source of Iranian prices, patient retail prices, stock availability, dosing, or treatment recommendations.

## Sources and definitions

1. **openFDA NDC** — official product-directory records, updated frequently. The NDC listing is not proof of FDA approval. https://open.fda.gov/apis/drug/ndc/
2. **CMS NADAC** — US National Average Drug Acquisition Cost **per unit**, posted weekly; **not** pharmacy retail price or Iranian price. Download an official CSV from https://data.medicaid.gov/dataset/fbb83258-11c7-47f5-8b18-5f8e79f7e704
3. **Iran TTAC** — candidate for later integration, only after verifying an authorized, stable public data route, permitted usage, exact price definitions, and terms. Not connected in MVP.

Do **not** join the FDA product-level NDC with the CMS 11-digit NDC by name alone. These exports are deliberately separate until identifier normalization and unit/package equivalence have been validated.

## Run

From repository root with Python 3.10+:

```bash
python examples/drug_market_monitor.py --drug ibuprofen
python examples/drug_market_monitor.py --drug ibuprofen --nadac-csv /path/to/official-nadac.csv
python examples/drug_market_monitor.py --drug ibuprofen --nadac-csv /path/to/official-nadac.csv --offline
python -m unittest discover -s examples -p 'test_drug_market_monitor.py'
```

Outputs: `output/drug_market/products.csv` and, only if an official NADAC CSV is supplied, `output/drug_market/nadac_costs.csv`. Fields include source URL, collection UTC timestamp, currency, price type, and effective date. The tests use **synthetic fixture values**; they do not represent measured medicine prices.

For testing, the openFDA API requires network access. The NADAC path uses an *official downloaded CSV* rather than scraping heavy pages or bypassing defenses. Avoid aggressive crawling and honor each service's policies.

## Next milestones

- Verify authorized Iran-source access, currency (rial/toman) and unit definitions
- Validate identifier normalization, NDC package mappings, and duplicate handling
- Persist history and calculate changes **only** between comparable price records
- Add scheduled polling, error alerts, human QA, and provenance dashboards
