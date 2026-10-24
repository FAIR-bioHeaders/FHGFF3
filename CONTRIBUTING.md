# Contributing

This repository has two scopes. Make your change in the right one.

## FAIR FHGFF3 header contract (`header/`)

Development of the FAIR FHGFF3 header happens here in the `header/` tree and is
coordinated into the shared publication repository. The final model, generated
schema, documentation, examples and conformance vectors publish in
[FAIR-bioHeaders-Specification](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification);
this repository publishes nothing.

- Model: `header/model/fhgff3_linkml.yml` (imports the shared core).
- Documentation: `header/docs/FHGFF3.md`.
- Examples and vectors: `header/examples/fhgff3/`, `header/conformance/`.
- Provenance: `header/PROVENANCE.md`; `header/provenance.json` pins the shared
  revision. Run `python3 scripts/check_header_parity.py` (also run in CI).

The `header/` files are byte-exact copies. Do not edit them in place to make a
contract change: propose and review the change in the shared repository, then
re-import it byte-for-byte and update the pin as described in
`header/PROVENANCE.md`. Any new field, constraint, enum value or changed meaning
is a schema addition with its own review cycle — not a routine edit.

A header never makes the GFF3 features valid. Feature and biology checks belong in
[gff3-validator](https://github.com/FAIR-bioHeaders/gff3-validator); header
processing and parent verification belong in
[FAIR-bioHeaders-Tools](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools).
The archived FHT-File-Converter is not an active dependency.

Family layout is tracked in
[FAIR-bioHeaders-Specification#107](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/issues/107)
and header follow-ups in [FHGFF3#2](https://github.com/FAIR-bioHeaders/FHGFF3/issues/2).

## Inherited GFF3 feature model (`src/`)

Fork this repo and check out on command line

Make edits in src/schema

Use `make` to build targets.

This tree is inherited from the biodatamodels/gff-schema fork. Its upstream
permissions are unresolved ([FHGFF3#3](https://github.com/FAIR-bioHeaders/FHGFF3/issues/3));
do not reuse it or fold it into the `header/` tree until that is settled.

## Checks before proposing a change

Follow the [CI guide](ci/README.md) for exact commands and CI scope. Run the local
documentation checks for guidance changes, the existing unittest suite for test
or tooling changes, and header parity before proposing a pin update. The shared
publication checkout owns schema generation and drift baselines. No inherited
model generation is enabled while its upstream permissions remain unresolved.

## Contribution licensing

FAIR BioHeaders contributions use [MPL-2.0](LICENSE), subject to the scope and preserved permissions stated there. This does **not** license the inherited biodatamodels/gff-schema material: no upstream root license was present in the inspected checkout, and upstream permissions remain to be clarified. New contributions must have the rights needed for their declared license; retain source notices.
