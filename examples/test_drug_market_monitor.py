"""Offline tests: python -m unittest discover -s examples -p 'test_drug_market_monitor.py'"""
import csv
import tempfile
import unittest
from pathlib import Path

from drug_market_monitor import COLUMNS, export_csv, read_nadac_csv


class DrugMonitorTests(unittest.TestCase):
    def test_nadac_csv_filters_and_preserves_cost_units(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "nadac.csv"
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "NDC Description", "NDC", "NADAC Per Unit", "Pricing Unit", "Effective Date"])
                writer.writeheader()
                writer.writerow({"NDC Description": "IBUPROFEN 200 MG", "NDC": "00000000001",
                                 "NADAC Per Unit": "0.1234", "Pricing Unit": "EA",
                                 "Effective Date": "10/01/2026"})
                writer.writerow({"NDC Description": "ACETAMINOPHEN", "NDC": "00000000002",
                                 "NADAC Per Unit": "0.15", "Pricing Unit": "EA",
                                 "Effective Date": "10/01/2026"})
            rows = read_nadac_csv(source, "ibuprofen")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["price_value"], "0.1234")
            self.assertEqual(rows[0]["price_type"], "US_NADAC_PHARMACY_ACQUISITION_PER_UNIT")
            out = Path(folder) / "out.csv"
            export_csv(rows, out)
            with out.open(encoding="utf-8-sig", newline="") as handle:
                self.assertEqual(list(csv.DictReader(handle))[0]["currency"], "USD")

    def test_header_only_when_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "empty.csv"
            export_csv([], dest)
            self.assertEqual(dest.read_text(encoding="utf-8-sig").strip(), ",".join(COLUMNS))


if __name__ == "__main__":
    unittest.main()
