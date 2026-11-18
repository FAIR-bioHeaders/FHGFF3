"""Tests for scripts/check_header_parity.py (standard library only)."""

import json
import subprocess
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

    def test_local_files_are_the_documented_set(self):
        self.assertEqual(parity.LOCAL_FILES, {
            "header/README.md",
            "header/PROVENANCE.md",
            "header/provenance.json",
            "header/docs/README.md",
            "header/conformance/README.md",
        })

    def test_unlisted_file_outside_the_copied_directories_fails(self):
        self.write("header/README.md")
        self.write("header/notes.md")
        self.write("header/conformance/extra.txt")
        self.write("header/new-dir/file.yml")
        errors = self.extras({})
        self.assertEqual(errors, [
            "unlisted file: header/conformance/extra.txt",
            "unlisted file: header/new-dir/file.yml",
            "unlisted file: header/notes.md",
        ])

    def test_copied_entry_outside_header_fails(self):
        errors = self.extras({"docs/FHGFF3.md": {}})
        self.assertEqual(errors, ["copied file outside header/: docs/FHGFF3.md"])

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


class RefTest(unittest.TestCase):
    """source.ref must be a release tag that resolves to source.commit (#241)."""

    def prov(self, ref, commit="0" * 40):
        return {"source": {"ref": ref, "commit": commit}}

    def test_release_tag_ref_passes(self):
        self.assertEqual(parity.check_ref(self.prov("v0.6.0")), [])

    def test_branch_or_missing_ref_fails(self):
        for ref in ("main", "master", "0ae18b00", "v0.6", "v0.6.0-rc1", "", None):
            with self.subTest(ref=ref):
                self.assertEqual(len(parity.check_ref(self.prov(ref))), 1)
        self.assertEqual(len(parity.check_ref({"source": {"commit": "0" * 40}})), 1)

    def test_repository_pin_is_a_release_tag(self):
        prov = json.loads((ROOT / "header" / "provenance.json").read_text())
        self.assertEqual(parity.check_ref(prov), [])

    def make_repo(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        repo = Path(temp.name)

        def git(*args):
            return subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                 "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *args],
                check=True, capture_output=True, text=True).stdout.strip()

        git("init", "-q")
        git("commit", "-q", "--allow-empty", "-m", "one")
        first = git("rev-parse", "HEAD")
        git("tag", "-a", "v0.6.0", "-m", "release")
        git("commit", "-q", "--allow-empty", "-m", "two")
        second = git("rev-parse", "HEAD")
        return repo, first, second

    def test_tag_resolving_to_the_pinned_commit_passes(self):
        repo, first, _ = self.make_repo()
        self.assertEqual(
            parity.check_ref_resolves(self.prov("v0.6.0", first), repo), [])

    def test_tag_resolving_elsewhere_fails(self):
        repo, _, second = self.make_repo()
        errors = parity.check_ref_resolves(self.prov("v0.6.0", second), repo)
        self.assertEqual(len(errors), 1)
        self.assertIn("not the pinned commit", errors[0])

    def test_missing_tag_fails(self):
        repo, first, _ = self.make_repo()
        errors = parity.check_ref_resolves(self.prov("v0.5.0", first), repo)
        self.assertEqual(len(errors), 1)
        self.assertIn("tag v0.5.0 is not in", errors[0])


if __name__ == "__main__":
    unittest.main()
