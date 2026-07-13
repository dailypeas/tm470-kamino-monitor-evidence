import json
import tempfile
import unittest
from pathlib import Path

from kamino_monitor.cli import main


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_fixture_command_writes_json_and_csv(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            code = main(
                [
                    "analyse-fixture",
                    "--input",
                    str(ROOT / "data/raw/fixtures/synthetic-triggering.json"),
                    "--output-dir",
                    str(output),
                ]
            )
            self.assertEqual(code, 0)
            self.assertTrue((output / "analysis.csv").exists())
            document = json.loads((output / "analysis.json").read_text())
            self.assertEqual(document["summary"]["priority_counts"]["elevated"], 1)

    def test_malformed_json_returns_controlled_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "bad.json"
            source.write_text("{", encoding="utf-8")
            code = main(
                ["analyse-fixture", "--input", str(source), "--output-dir", str(Path(temporary) / "out")]
            )
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
