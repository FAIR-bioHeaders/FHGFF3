"""Check owned Markdown paths offline; never rewrite pinned or inherited files."""

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def owned_paths(root=ROOT):
    """Use the same positive scope as Markdown lint and external links."""
    config = json.loads((root / ".markdownlint-cli2.jsonc").read_text())
    return sorted({p for pattern in config["globs"] for p in root.glob(pattern)
                   if p.is_file()})


def check_file(path, root=ROOT):
    errors = []
    text = path.read_text(encoding="utf-8")
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"{path}:{number}: trailing whitespace")
        if re.match(r"^(?:<{7}|={7}|>{7}|\|{7})(?:\s|$)", line):
            errors.append(f"{path}:{number}: unresolved conflict marker")
    # Ignore code samples. Fragment identifiers need a Markdown renderer and
    # are outside this deliberately small file-target check.
    prose = re.sub(r"(?ms)^ *(`{3,}|~{3,})[^\n]*\n.*?^ *\1 *$", "", text)
    prose = re.sub(r"(`+)[^`\n]*?\1", "", prose)
    links = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", prose)
    links += re.findall(r"(?m)^\s*\[[^\]]+\]:\s*(\S+)", prose)
    links += re.findall(r"<(\.?\.?/[^<>\s]+)>", prose)
    for target in links:
        target = target.strip()
        target = (target[1:].split(">", 1)[0] if target.startswith("<")
                  else target.split()[0] if target else "")
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        relative = unquote(parts.path)
        resolved = (root / relative.lstrip("/") if relative.startswith("/")
                    else path.parent / relative).resolve()
        if not resolved.is_relative_to(root.resolve()):
            errors.append(f"{path}: local link escapes repository: {target}")
        elif not resolved.exists():
            errors.append(f"{path}: missing local target: {target}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list owned paths only")
    args = parser.parse_args()
    paths = owned_paths()
    if not paths:
        parser.error("no owned documentation found")
    if args.list:
        print("\n".join(str(p.relative_to(ROOT)) for p in paths))
        return 0
    errors = [e for path in paths for e in check_file(path)]
    for error in errors:
        print(error)
    print(f"Checked {len(paths)} owned Markdown files: local file targets, whitespace "
          "and conflict markers (no network or fragment checks).")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
