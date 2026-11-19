# GFF Schema

This repository holds two distinct things. Keep them separate.

| Scope | Paths | What it is |
| --- | --- | --- |
| **Inherited GFF3 feature model** | `src/`, `jsonschema/`, `python/`, `rdf/`, `owl/`, `shex/`, `graphql/`, `csv/` | The forked biodatamodels/gff-schema draft feature model. It is **not** the FAIR header contract, and it is excluded from downstream reuse under the [maintainer no-reuse decision](#inherited-material-no-reuse-boundary). |
| **FAIR FHGFF3 header contract** | `header/` | Development copy of the independently authored FAIR provenance header around GFF3: model, documentation, examples and conformance vectors. |

## The inherited GFF3 feature model

This is a repository for a DRAFT of a computable schema for GFF3

It is designed to separate out the *datamodel* from the *serialization* (TSV)

See [https://biodatamodels.github.io/gff-schema/](https://biodatamodels.github.io/gff-schema/) for more docs

Edit `src/schema/gff.yaml` and build with `make` (`make gen` builds artifacts
under `target/`; `make stage` copies generated formats into the tracked output
directories). Do not hand-edit the generated Python, JSON Schema, RDF/OWL, ShEx,
GraphQL or documentation output; those are not primary sources. `make clean`
removes both `target/` and `docs/`. This tree is inherited from the
biodatamodels/gff-schema fork; read the [licensing section](#licensing) and
[no-reuse boundary](#inherited-material-no-reuse-boundary). The build commands
describe the inherited tree; they do not authorize reuse or distribution.

## The FAIR FHGFF3 header contract

`header/` is the development copy of the **FAIR FHGFF3 header**: a provenance
header (`#~` lines) placed around ordinary GFF3, recording which genome the
annotation's coordinates refer to and how the annotation was made. It is
independently authored FAIR BioHeaders work, not derived from the inherited
feature model. Start with [`header/README.md`](header/README.md).

- **Final artifacts publish in
  [FAIR-bioHeaders-Specification](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification).**
  The model (`fhgff3_linkml.yml`), the generated schema (`fhgff3.json`), the
  documentation, examples and vectors live there. Released schemas are served
  from `https://w3id.org/fair-bioheaders/fhgff3/vX.Y.Z` — currently
  [v0.6.0](https://w3id.org/fair-bioheaders/fhgff3/v0.6.0), `schemaVersion`
  `"1.2"`. This repository publishes no schemas.
- **Pinned provenance:** `header/` is a byte-for-byte copy pinned to a recorded
  commit of the shared repository ([`header/provenance.json`](header/provenance.json),
  [`header/PROVENANCE.md`](header/PROVENANCE.md)). `scripts/check_header_parity.py`
  runs in CI and fails if the copy drifts.
- **Active toolkit:**
  [FAIR-bioHeaders-Tools](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools)
  (`pip install fair-bioheaders`) adds, verifies and strips FAIR headers,
  including FHGFF3.
- **Feature and biology checks:**
  [gff3-validator](https://github.com/FAIR-bioHeaders/gff3-validator) validates
  the GFF3 features themselves. A header never makes the features valid.
- The former FHR-File-Converter repository name redirects to FAIR-bioHeaders-Tools.

### Contributor checks

Run `python3 -m unittest discover -s tests -v`,
`python3 scripts/check_header_parity.py`, `python3 scripts/check_docs.py`, and
`npx markdownlint-cli2@0.23.2 --config .markdownlint-cli2.jsonc` from this root.
See [the CI guide](ci/README.md) for the exact shared conformance and external-link
commands, runtime versions, owned-documentation scope and inherited-model boundary.
These checks also run for documentation-only PRs.

### Issue links

- Family layout tracker:
  [FAIR-bioHeaders-Specification#107](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/issues/107)
- FHGFF3 header tracker:
  [FHGFF3#2](https://github.com/FAIR-bioHeaders/FHGFF3/issues/2)
- Inherited gff-schema licensing:
  [FHGFF3#3](https://github.com/FAIR-bioHeaders/FHGFF3/issues/3)

## Licensing

[![FAIR BioHeaders contributions: MPL-2.0](https://img.shields.io/badge/FAIR_BioHeaders_contributions-MPL--2.0-blue.svg)](LICENSE)

FAIR BioHeaders contributions use [MPL-2.0](LICENSE), subject to the scope and preserved permissions stated there. This does **not** license the inherited biodatamodels/gff-schema material: no upstream root license was present in the inspected checkout, and upstream permissions remain to be clarified.

The files under `header/` come from the MPL-2.0 shared publication repository and
are new FAIR BioHeaders work here; the inherited feature model is excluded from
that grant, and no file under `header/` is copied from it. The `LICENSE`
inventory records the copied header scope through its upstream provenance.
Historical notices are preserved.

### Inherited material: no-reuse boundary

David selected the documented no-reuse disposition for [FHGFF3#3](https://github.com/FAIR-bioHeaders/FHGFF3/issues/3)
in [Round 14 decision D11](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/issues/211#issuecomment-7017854934).
The inherited snapshot is retained as history and reference material. It is
excluded from FAIR BioHeaders downstream reuse, packaging and distribution as
reusable schema/code until applicable permission is evidenced and a new reviewed
scope decision is made. It is not a Project 9 dependency of the independently
authored header. No upstream permission has been obtained by this decision.

The exact inspected import is commit
[`9c8cf644e93d5dbfeb3662dc03183d8ed7b830de`](https://github.com/FAIR-bioHeaders/FHGFF3/commit/9c8cf644e93d5dbfeb3662dc03183d8ed7b830de)
(November 6, 2024). Its complete 27-path inventory is recorded in
[LICENSE](LICENSE), including imported README/CONTRIBUTING portions, the feature
model and generated artifacts. Git records Adam Wright as the upload commit's
author; this is import provenance, not proof of original authorship or licensing
rights. Original rights-holder authorship and an applicable upstream grant have
not been established. The [existing upstream request](https://github.com/biodatamodels/gff-schema/issues/3)
remains evidence to consult if reuse is reconsidered; no contact is required to
complete the no-reuse disposition.

Retain the snapshot, source history and all existing file-level notices. Do not
apply this repository's MPL notice to the inherited material, delete it to imply
resolution, or claim that the whole fork is licensed for reuse. Any replacement
or revived downstream reuse requires its own rights/provenance review. The
independent `header/` copy retains the shared publication source's permissions
and notices as recorded in [its provenance](header/PROVENANCE.md).
