"""Failure cases for the owned-documentation CI gate."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "check_docs", Path(__file__).resolve().parents[1] / "scripts/check_docs.py")
docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(docs)


class DocumentationChecks(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "exists here.md").write_text("# Target\n")
            path = root / "README.md"
            path.write_text(text)
            return docs.check_file(path, root)

    def test_missing_and_escaping_links(self):
        errors = self.check("[missing](missing.md)\n[x]: ../escape.md\n")
        self.assertTrue(any("missing local target" in e for e in errors))
        self.assertTrue(any("escapes repository" in e for e in errors))

    def test_valid_links_and_samples(self):
        self.assertEqual([], self.check(
            '[ok](<exists here.md>)\n[encoded](exists%20here.md#section)\n'
            '[remote](https://example.org/no-local-file)\n[anchor](#section)\n'
            '`[example](missing.md)`\n```md\n[sample](absent.md)\n```\n'))

    def test_conflicts_and_whitespace(self):
        errors = self.check("text \n<<<<<<< ours\n=======\n>>>>>>> theirs\n")
        self.assertEqual(4, len(errors))

    def test_scope_excludes_pinned_and_inherited_documents(self):
        paths = {str(p.relative_to(docs.ROOT)) for p in docs.owned_paths()}
        self.assertIn("AGENTS.md", paths)
        self.assertIn("header/docs/README.md", paths)
        self.assertNotIn("header/docs/FHGFF3.md", paths)
        self.assertNotIn("MAINTAINERS.md", paths)


if __name__ == "__main__":
    unittest.main()
