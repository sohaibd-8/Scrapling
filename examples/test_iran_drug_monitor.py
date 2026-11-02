import tempfile
import unittest
from pathlib import Path
from iran_drug_monitor import load, compare, FIELDS

class MonitorTests(unittest.TestCase):
    def test_validated_changes(self):
        base={"irc":"1234567890","drug_name":"SAMPLE - NOT REAL","brand":"","manufacturer":"",
              "form":"tablet","strength":"test","pack_size":"20 tablets",
              "price_rial":"10000","price_type":"official_consumer_price",
              "observed_at":"2026-11-01T10:00:00+03:30","source_url":"https://www.ttac.ir/"}
        later=dict(base,price_rial="12000")
        result=compare([base],[later])
        self.assertEqual(result[0]["change_percent"],"20.00")
    def test_empty_csv_header(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"empty.csv"
            f.write_text(",".join(FIELDS)+"\n",encoding="utf-8")
            self.assertEqual(load(f),[])

if __name__=="__main__":
    unittest.main()
