"""Tests for scripts/check_header_parity.py (standard library only)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_header_parity as parity  # noqa: E402


class StrictDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def write(self, rel):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")

    def extras(self, listed):
        with mock.patch.object(parity, "ROOT", self.root):
            return parity.check_extras(listed)

    def test_docs_is_a_strict_directory(self):
        self.assertIn("header/docs", parity.STRICT_DIRS)

    def test_allowed_docs_readme_passes(self):
        self.write("header/docs/FHGFF3.md")
        self.write("header/docs/README.md")
        self.assertEqual(self.extras({"header/docs/FHGFF3.md": {}}), [])

    def test_unexpected_docs_file_fails(self):
        self.write("header/docs/FHGFF3.md")
        self.write("header/docs/README.md")
        self.write("header/docs/notes.md")
        errors = self.extras({"header/docs/FHGFF3.md": {}})
        self.assertEqual(len(errors), 1)
        self.assertIn("unlisted file: header/docs/notes.md", errors[0])

    def test_unexpected_file_in_copied_directory_fails(self):
        self.write("header/model/fhgff3_linkml.yml")
        self.write("header/model/extra.yml")
        errors = self.extras({"header/model/fhgff3_linkml.yml": {}})
        self.assertEqual(len(errors), 1)
        self.assertIn("unlisted file: header/model/extra.yml", errors[0])

    def test_repository_docs_directory_passes(self):
        prov = json.loads((ROOT / "header" / "provenance.json").read_text())
        listed = {entry["local"]: entry for entry in prov["copied"]}
        self.assertEqual(parity.check_extras(listed), [])


if __name__ == "__main__":
    unittest.main()
