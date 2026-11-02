# TTAC public-page reader (Scrapling)

**Scope: Iran only, publicly accessible TTAC pages only.** This is a selector-based page reader, *not* an API. No login, authentication reuse, CAPTCHA solving, anti-bot bypass, proxy rotation or high-volume crawling is implemented.

Source discovery: government health communications describe navigating **ttac.ir → mobile applications → web version → drug shortage search**, which may display drug metadata and prices. The exact public result-page URL, live DOM selectors, and automated access permission have **not been independently verified**. Do not invent them. Access may differ by user and may be blocked.

Try a single public landing page:

```bash
pip install -e .
python examples/ttac_public_reader.py --url https://www.ttac.ir/ --mode http
```

If you have verified a public result URL and its CSS selectors, enter the actual values:

```bash
python examples/ttac_public_reader.py --url 'https://<real-ttac-host>/<real-public-result>' --mode browser --row-selector '<row>' --name-selector '<name>' --price-selector '<price>'
```

Replace placeholders with real inspected values. The reader writes only `inspection.json` (title, headings and link count); when selectors are supplied it also writes `unverified_rows.csv`. No data is called official pricing without independent price-unit, package, IRC and date verification. Avoid scraping any page that requires login or displays personal data. Respect site terms and immediately stop on access restrictions.

Validated CSV snapshots can then be processed separately by `iran_drug_monitor.py`. The raw outputs cannot be directly imported as validated prices.

References: https://www.ttac.ir/ and https://scrapling.readthedocs.io/en/latest/
