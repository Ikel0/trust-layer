import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from server import profile_world_bank_population

class TrustLayerTest(unittest.TestCase):
    def test_sample_dataset_fails_with_expected_issues(self):
        with tempfile.TemporaryDirectory() as output:
            result = subprocess.run(["python3", "src/run_quality.py", "--output", output], cwd=ROOT, capture_output=True, text=True)
            report = json.loads((Path(output) / "report.json").read_text())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(len(report["issues"]), 4)

    def test_world_bank_profile_keeps_provenance_and_missing_values(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self):
                return b'[{"page":1},[{"date":"2025","value":68720337},{"date":"2024","value":null}]]'

        with patch("server.urlopen", return_value=Response()):
            report = profile_world_bank_population()
        self.assertTrue(report["live"])
        self.assertEqual(report["profile"]["rows"], 2)
        self.assertEqual(report["profile"]["missing_values"], 1)
        self.assertEqual(report["records"][0]["year"], "2025")

if __name__ == "__main__": unittest.main()
