#!/usr/bin/env python3
"""Check the FAIR FHGFF3 header development copy against its pinned upstream.

``header/`` holds a development copy of the FHGFF3 header contract (model,
documentation, examples and conformance vectors) taken byte-for-byte from a
pinned FAIR-bioHeaders-Specification revision. ``header/provenance.json`` records
that revision and the SHA-256 digest of every copied file.

Without options this checks each copied file against the recorded digest, so it
needs only the standard library and works offline. With ``--upstream PATH`` it
also reads the pinned commit from a checkout of FAIR-bioHeaders-Specification and
compares the actual upstream bytes, which is what CI does. If an upstream
checkout is found next to this one (or in ``FAIR_BIOHEADERS_SPECIFICATION``) the
live comparison runs automatically; ``--no-upstream`` forces the digest-only
check.

Any divergence (a changed, missing or unlisted file, or a wrong pin) exits
non-zero. Nothing here edits the copy; see header/PROVENANCE.md for how to update
it deliberately.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = ROOT / "header" / "provenance.json"
# Directories that must contain exactly the copied files, no more and no less.
STRICT_DIRS = (
    "header/model",
    "header/docs",
    "header/examples/fhgff3",
    "header/conformance/valid",
    "header/conformance/invalid",
)
# Local-only files that are allowed alongside the copied files in a strict
# directory. header/docs/README.md is the landing page and link map for the
# byte-exact copy; it is intentionally not part of the pinned set.
ALLOWED_EXTRAS = frozenset({
    "header/docs/README.md",
})
UPSTREAM_ENV = "FAIR_BIOHEADERS_SPECIFICATION"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_provenance():
    try:
        data = json.loads(PROVENANCE.read_text())
    except FileNotFoundError:
        sys.exit(f"error: {PROVENANCE} is missing")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {PROVENANCE} is not valid JSON: {exc}")
    return data


def check_local(prov):
    """Compare every copied file with its recorded digest."""
    errors = []
    listed = {}
    for entry in prov.get("copied", []):
        local = entry["local"]
        listed[local] = entry
        path = ROOT / local
        if not path.is_file():
            errors.append(f"missing: {local}")
            continue
        size = path.stat().st_size
        if size != entry["size"]:
            errors.append(
                f"size differs: {local} (local {size}, pinned {entry['size']})")
        digest = sha256(path)
        if digest != entry["sha256"]:
            errors.append(
                f"content differs: {local} (local {digest[:12]}..., "
                f"pinned {entry['sha256'][:12]}...)")
    return errors, listed


def check_extras(listed):
    """Fail on files present in the strict directories but not in provenance."""
    errors = []
    for rel_dir in STRICT_DIRS:
        directory = ROOT / rel_dir
        if not directory.is_dir():
            continue
        expected = {p for p in listed if p.startswith(rel_dir + "/")}
        actual = {
            str(p.relative_to(ROOT))
            for p in directory.rglob("*")
            if p.is_file()
        }
        for extra in sorted(actual - expected - ALLOWED_EXTRAS):
            errors.append(f"unlisted file: {extra}")
    return errors


def find_upstream(explicit):
    if explicit:
        path = Path(explicit).expanduser()
        if not (path / ".git").exists():
            sys.exit(f"error: --upstream {explicit} is not a git checkout")
        return path
    env = os.environ.get(UPSTREAM_ENV)
    if env:
        path = Path(env).expanduser()
        if (path / ".git").exists():
            return path
    for candidate in (
        ROOT.parent / "FAIR-bioHeaders-Specification",
        ROOT.parent.parent / "FAIR-bioHeaders-Specification",
    ):
        if (candidate / ".git").exists():
            return candidate
    return None


def git_show(repo, commit, path):
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{commit}:{path}"],
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def check_upstream(prov, repo):
    """Compare the pinned commit's bytes with the recorded digests and the copy."""
    errors = []
    commit = prov["source"]["commit"]
    exists = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True,
    )
    if exists.returncode != 0:
        return [f"pinned commit {commit[:12]}... is not in {repo}"], 0

    checked = 0
    for entry in prov.get("copied", []) + prov.get("imports", []):
        upstream = entry["upstream"]
        data = git_show(repo, commit, upstream)
        if data is None:
            errors.append(f"pinned commit has no {upstream}")
            continue
        digest = hashlib.sha256(data).hexdigest()
        if digest != entry["sha256"]:
            errors.append(
                f"pinned {upstream} does not match its recorded digest")
        if "local" in entry:
            local = ROOT / entry["local"]
            if local.is_file() and local.read_bytes() != data:
                errors.append(
                    f"local {entry['local']} differs from pinned {upstream}")
        checked += 1
    return errors, checked


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--upstream", metavar="PATH",
        help="FAIR-bioHeaders-Specification checkout to compare against")
    parser.add_argument(
        "--no-upstream", action="store_true",
        help="only check the recorded digests, even if a checkout is available")
    args = parser.parse_args(argv)

    prov = load_provenance()
    commit = prov["source"]["commit"]
    print(f"header parity: pinned {prov['source']['repository']} {commit}")
    print(f"  {len(prov.get('copied', []))} copied files, "
          f"{len(prov.get('imports', []))} recorded imports")

    errors, listed = check_local(prov)
    errors += check_extras(listed)

    upstream = None if args.no_upstream else find_upstream(args.upstream)
    if upstream is not None:
        upstream_errors, checked = check_upstream(prov, upstream)
        errors += upstream_errors
        print(f"  compared against pinned bytes in {upstream} "
              f"({checked} files)")
    elif args.upstream:
        sys.exit("error: --upstream was given but is not usable")
    else:
        print("  no upstream checkout found; checked recorded digests only")

    if errors:
        print("\nFAIL: the header development copy has diverged:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("\nOK: the header development copy matches the pinned revision.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
