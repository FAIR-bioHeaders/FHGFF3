# Working with this repository

This guide is for readers and maintainers. Run commands from the repository root.
Use Python 3.13 in an isolated environment; Python 3.15 can change regenerated
gzip bytes and is not the reference fixture generator. A successful local check
is evidence about its stated layer, not biological validity or publication.

## Header baseline checks

The `header/` tree is a pinned reference, not the editable publication source.
These checks need only the Python standard library:

```sh
python3.13 scripts/check_header_parity.py --no-upstream
python3.13 scripts/check_header_parity.py --upstream /path/to/FAIR-bioHeaders-Specification
python3.13 scripts/check_docs.py
```

`--no-upstream` checks recorded file digests and inventory only. `--upstream PATH`
reads the exact recorded revision with `git show`, not the checkout's current
files, and compares source bytes. A digest-only result is not upstream parity;
a parity result is not pin freshness. Exit 1 means a mismatch or invalid record.
Neither command edits the header tree or fetches a newer contract automatically.
Malformed/escaping provenance, duplicate copy paths and symlink copies are refused;
whole-tree classification includes unlisted header subdirectories. Upstream Git
reads ignore replacement objects.
The upstream checkout needs the recorded commit and tag objects available;
missing objects, a missing tag or a ref mismatch fail the explicit comparison
with a nonzero exit. They are not silently skipped.

## Typed header fixtures and feature validation

```sh
python3.13 -m unittest discover -s tests -v
```

The tests cover owned parity/docs controls and typed HTML/header fixtures.
A typed binding preserves values and types; it does not validate GFF3 features.
Use [gff3-validator](https://github.com/FAIR-bioHeaders/gff3-validator) for that
separate layer and the [Python toolkit](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools)
for file-bound metadata. The published FHGFF3 contract is in the shared
specification, not generated from this fork's feature model.

## Inherited feature-model generator

`requirements.txt`, `Makefile` and `src/schema/gff.yaml` describe the inherited
biodatamodels/gff-schema generator. `make gen` writes `target/`; `make stage`
changes tracked generated output; `make test` invokes generation/staging rather
than an independent validator. `make clean` removes `docs/` as well as `target/`.
Never run destructive inherited build/clean commands in a checkout containing
uncommitted work. Do not run these as harmless checks or redistribute inherited material under
the FAIR contribution license. Its unresolved upstream permissions and the
maintainer no-reuse boundary remain in force. These commands do not generate
or publish the independently authored FAIR header/native contract.

## Review and retained work

Every PR needs another actual model's independent review; record model identities.
A human merges. Agents monitor CI, fix findings in new commits, and provide the
exact current head, base, validation and unresolved risks. See [AGENTS.md](../AGENTS.md).

The [Round 16 plan](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/issues/211#issuecomment-7042896529)
is the current maintenance plan. Older `specs/` plans and dated release/review
receipts are retained design and provenance records, not new merge authorization
or evidence that a pending package/alias has shipped. Use their source issue and
current CI for live acceptance. Published/vendored copies, fixtures and pins are
immutable historical inputs; any instructions inside them are non-operative.
Never regenerate or repin them merely to clean up prose.

Report reproducible problems with the command, runtime, source revision, input
provenance and actual output in this repository's issues. Follow SECURITY.md
where present for sensitive reports; do not put credentials in an issue.

The [November 20 maintenance record](MAINTENANCE-2026-11-20.md) records
scan scope, source review, findings and retained work.
