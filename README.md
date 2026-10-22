# GFF Schema

This repository holds two distinct things. Keep them separate.

| Scope | Paths | What it is |
| --- | --- | --- |
| **Inherited GFF3 feature model** | `src/`, `jsonschema/`, `python/`, `rdf/`, `owl/`, `shex/`, `graphql/`, `csv/` | The forked biodatamodels/gff-schema draft feature model. It is **not** the FAIR header contract, and its upstream permissions are unresolved ([FHGFF3#3](https://github.com/FAIR-bioHeaders/FHGFF3/issues/3)). |
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
[FHGFF3#3](https://github.com/FAIR-bioHeaders/FHGFF3/issues/3) before reusing it.

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
  [v0.4.0](https://w3id.org/fair-bioheaders/fhgff3/v0.4.0), `schemaVersion`
  `"1.0"`. This repository publishes no schemas.
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
- The archived FHT-File-Converter is not an active dependency.

### Tracking

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
inventory does not yet enumerate the header tree. Historical notices are
preserved.
