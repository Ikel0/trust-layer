import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TrustLayerTest(unittest.TestCase):
    def test_sample_dataset_fails_with_expected_issues(self):
        with tempfile.TemporaryDirectory() as output:
            result = subprocess.run(["python3", "src/run_quality.py", "--output", output], cwd=ROOT, capture_output=True, text=True)
            report = json.loads((Path(output) / "report.json").read_text())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(len(report["issues"]), 4)

if __name__ == "__main__": unittest.main()
