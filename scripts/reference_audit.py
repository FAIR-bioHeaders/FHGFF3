#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Audit CURRENT owning declarations with one immutable shared checker; never repin."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = 'FAIR-bioHeaders/FAIR-bioHeaders-Specification'
CONSUMER = 'FAIR-bioHeaders/FHGFF3'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(root, name):
    data = json.loads((root / name).read_text())
    if not isinstance(data, dict):
        raise ValueError(name + ': expected object')
    return data


def measured_file(local, upstream, sha, **extra):
    if sha not in (None, '') and (not isinstance(sha, str) or not re.fullmatch('[0-9a-f]{64}', sha)):
        raise ValueError(str(local or upstream) + ': unusable recorded digest')
    return dict(local=local, path=upstream, sha256=sha, **extra)


def reference(identity, cls, revision, files, commit=None, **extra):
    if revision not in (None, '') and not isinstance(revision, str):
        raise ValueError(identity + ': unusable recorded revision')
    if commit not in (None, '') and (not isinstance(commit, str) or not re.fullmatch('[0-9a-f]{40}', commit)):
        raise ValueError(identity + ': unusable recorded commit')
    row = dict(id=identity, consumer=CONSUMER, repository=AUTHORITY, **{'class': cls},
               revision=revision, revisionKind='tag' if not revision or revision.startswith('v') else 'commit' if re.fullmatch('[0-9a-f]{40}', revision) else 'branch', files=files)
    if commit:
        row['commit'] = commit
    row.update(extra)
    return row


def validated_bindings(root, filename, wanted):
    """Accept each consumed binding/dependency once, as a top-level assignment."""
    tree = ast.parse((root / filename).read_text())
    assignments = {}
    candidates = {}
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
            candidates.setdefault(statement.targets[0].id, []).append(statement)
    needed = set(wanted)
    pending = list(wanted)
    while pending:
        name = pending.pop()
        for statement in candidates.get(name, []):
            for node in ast.walk(statement.value):
                if isinstance(node, ast.Name) and node.id not in needed:
                    needed.add(node.id)
                    pending.append(node.id)
    for name in needed:
        entries = candidates.get(name, [])
        if len(entries) > 1:
            raise ValueError(filename + ': reassigned source binding ' + name)
        if entries:
            assignments[name] = entries[0].value
    permitted = {id(entries[0].targets[0]) for name, entries in candidates.items() if name in needed and len(entries) == 1}
    for statement in tree.body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for node in ast.walk(statement):
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)) and node.id in needed and id(node) not in permitted:
                raise ValueError(filename + ': unsupported source binding write ' + node.id)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                base = node.func.value
                if isinstance(base, ast.Name) and base.id in needed:
                    raise ValueError(filename + ': unsupported source binding mutation ' + base.id)
            if isinstance(node, (ast.Subscript, ast.Attribute)) and isinstance(node.ctx, (ast.Store, ast.Del)):
                if any(isinstance(part, ast.Name) and part.id in needed for part in ast.walk(node)):
                    raise ValueError(filename + ': unsupported source binding mutation')
    return assignments


def literal_assignments(root, name, wanted):
    found = {key: ast.literal_eval(value) for key, value in validated_bindings(root, name, wanted).items() if key in wanted}
    if set(found) != set(wanted):
        raise ValueError(name + ': missing declared constants')
    return found


def require_authority(data, context):
    if isinstance(data, dict) and any(k in data for k in ('source', 'authority', 'source_repository', 'sourceUrl')):
        raise ValueError(context + ': unsupported nested source override')
    if not isinstance(data, dict) or data.get('repository') != AUTHORITY:
        raise ValueError(context + ': missing or unexpected source repository')
    if data.get('url') != 'https://github.com/' + AUTHORITY:
        raise ValueError(context + ': missing or unexpected source URL')


def reject_source_overrides(entry, context):
    for key in ('repository', 'url', 'source', 'authority', 'source_repository', 'sourceUrl'):
        if key in entry:
            raise ValueError(context + ': unsupported per-entry source override ' + key)


def string_declarations(root, filename, wanted):
    assignments = validated_bindings(root, filename, wanted)
    active = set()
    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name) and node.id in assignments and node.id not in active:
            active.add(node.id)
            try:
                return evaluate(assignments[node.id])
            finally:
                active.remove(node.id)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return evaluate(node.left) + evaluate(node.right)
        if isinstance(node, ast.JoinedStr):
            result = ''
            for item in node.values:
                if isinstance(item, ast.FormattedValue):
                    if item.conversion != -1 or item.format_spec is not None:
                        raise ValueError(filename + ': unsupported string conversion')
                    result += evaluate(item.value)
                else:
                    result += evaluate(item)
            return result
        raise ValueError(filename + ': unsupported source declaration expression')
    if not set(wanted) <= set(assignments):
        raise ValueError(filename + ': missing source declarations')
    return {name: evaluate(assignments[name]) for name in wanted}


def require_assignment(root, filename, name, expression):
    expected = ast.dump(ast.parse(expression, mode='eval').body)
    for node in ast.parse((root / filename).read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            if ast.dump(node.value) == expected:
                return
            break
    raise ValueError(filename + ': missing or unsupported ' + name + ' locator')


def declarations(root):
    name = 'header/provenance.json'
    data = load(root, name); source = data['source']
    require_authority(source, 'provenance source')
    if not isinstance(source, dict) or source.get('repository') != AUTHORITY:
        raise ValueError(name + ': missing or unexpected source repository')
    for entry in data['copied'] + data['imports']:
        reject_source_overrides(entry, 'header entry')
    files = [measured_file(e['local'], e.get('upstream'), e.get('sha256')) for e in data['copied']]
    rows = [reference('released-header-tree', 'copied-tree', source.get('ref'), files,
                      source.get('commit'), materialStatus='released', localTree='header',
                      sourcePatterns=['fhgff3_linkml.yml', 'docs/FHGFF3.md', 'examples/fhgff3/*',
                                      'conformance/valid/fhgff3-*', 'conformance/invalid/fhgff3-*'],
                      localExclusions=['header/PROVENANCE.md', 'header/README.md',
                                       'header/conformance/README.md', 'header/docs/README.md',
                                       'header/provenance.json'])]
    for entry in data['imports']:
        suite = entry.get('upstream') == 'conformance/manifest.json'
        rows.append(reference('import:' + str(entry.get('upstream')), 'conformance-suite' if suite else 'released-contract',
                              source.get('commit') if suite else source.get('ref'),
                              [measured_file(None, entry.get('upstream'), entry.get('sha256'))], source.get('commit')))
    return rows, [name], [
        'Full selected header scope and local documentation exclusions are declared; no inherited feature-model paths are reused.',
        'Imported models/rules/suite are checked at their own recorded authority, without pretending an unvendored import has a local byte copy.',
        'The inherited biodatamodels/gff-schema tree remains under the accepted no-reuse boundary, outside FAIR contract retrieval and this audit.']



def inventory(root=ROOT):
    rows, records, notes = declarations(root)
    if not rows:
        raise ValueError('No references declared')
    return dict(inventoryVersion=1, advisory=True, references=rows,
                generatedFrom=[dict(path=name, sha256=digest((root / name).read_bytes())) for name in records],
                coverageNotes=notes,
                coverageGaps=['Other consumer repositories require their own rollout; this port alone does not close shared #241.'])


def verified_checker(root, source):
    pin = load(root, 'references/checker.json')
    if any(k in pin for k in ('url', 'source', 'authority', 'source_repository', 'sourceUrl')):
        raise ValueError('Unsupported checker source attribution override')
    if pin.get('repository') != AUTHORITY or pin.get('path') != 'scripts/check_references.py':
        raise ValueError('Missing or unexpected checker source repository/path')
    if not isinstance(pin.get('commit'), str) or not re.fullmatch('[0-9a-f]{40}', pin['commit']):
        raise ValueError('Unusable immutable checker commit')
    if not isinstance(pin.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', pin['sha256']):
        raise ValueError('Unusable checker digest')
    if source.is_symlink() or (source / 'scripts').is_symlink() or (source / pin['path']).is_symlink():
        raise ValueError('Checker source path must not be a symlink')
    script = (source / pin['path']).resolve()
    if not script.is_relative_to(source.resolve()):
        raise ValueError('Checker path escapes the reviewed source checkout')
    actual = subprocess.check_output(['git', '--no-replace-objects', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != pin['commit']:
        raise ValueError('Checker checkout HEAD differs from the reviewed source pin')
    immutable = subprocess.check_output(['git', '--no-replace-objects', '-C', str(source), 'show', pin['commit'] + ':' + pin['path']])
    if script.read_bytes() != immutable:
        raise ValueError('Checker working bytes differ from the immutable commit')
    if digest(immutable) != pin['sha256']:
        raise ValueError('Checker source digest differs; refusing execution')
    return immutable


def checker_snapshot(root, source, directory):
    immutable = verified_checker(root, source)
    script = Path(directory) / 'verified-checker.py'
    script.write_bytes(immutable)
    script.chmod(0o400)
    return script


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checker-root', type=Path)
    parser.add_argument('--inventory-only', action='store_true')
    parser.add_argument('--inventory-output', type=Path)
    parser.add_argument('--checkout', action='append', default=[], metavar='OWNER/REPO=PATH')
    parser.add_argument('--strict', action='store_true', help='exit nonzero on findings (advisory by default)')
    args = parser.parse_args(argv)
    try:
        table = inventory()
        if args.inventory_output:
            args.inventory_output.write_text(json.dumps(table, indent=2) + '\n')
        if args.inventory_only:
            print(json.dumps(table, indent=2))
            return 0
        if not args.checker_root:
            parser.error('--checker-root is required for execution')
        with tempfile.TemporaryDirectory() as directory:
            script = checker_snapshot(ROOT, args.checker_root, directory)
            table_file = Path(directory) / 'inventory.json'
            table_file.write_text(json.dumps(table))
            command = [sys.executable, '-I', str(script), '--inventory', str(table_file),
                       '--consumer', CONSUMER, '--consumer-root', str(ROOT)]
            for mapping in args.checkout:
                command += ['--checkout', mapping]
            if args.strict:
                command.append('--exit-on-findings')
            return subprocess.run(command, check=False).returncode
    except (OSError, ValueError, KeyError, TypeError, AttributeError, SyntaxError, subprocess.CalledProcessError) as error:
        print(json.dumps(dict(advisory=True, status='UNUSABLE', error=str(error), wrotePins=[])))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
