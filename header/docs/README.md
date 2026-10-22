# FHGFF3 header documentation

`FHGFF3.md` in this directory is a **byte-for-byte development copy** of the
authoritative document in the shared publication repository, at the pinned
revision recorded in [`../provenance.json`](../provenance.json). It is kept here
so the header contract can be read and discussed next to the model and vectors.
Do not edit it: edit the shared file and re-import it deliberately (see
[`../PROVENANCE.md`](../PROVENANCE.md)).

Because the copy is byte-exact, **its relative links are resolved as if the file
still lived in the shared publication tree** (`docs/FHGFF3.md` there). Some of
those paths do not exist under `header/`. Use the table below to reach the
canonical upstream file, and the list after it to navigate the local copy. The
upstream URLs are pinned to commit
[`bdcaecf7`](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/tree/bdcaecf759b5b2be5fd61bf8f39368a7e3963315);
replace the commit with `main` for the current version.

## Where each link in `FHGFF3.md` goes

| Link target as written in the copy | Local destination | Canonical upstream |
| --- | --- | --- |
| `../specs/007-gff3-header/spec.md` | not present locally | [spec.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/specs/007-gff3-header/spec.md) |
| `../fhgff3_linkml.yml` | [`../model/fhgff3_linkml.yml`](../model/fhgff3_linkml.yml) | [fhgff3_linkml.yml](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/fhgff3_linkml.yml) |
| `../schemas/core.yaml` | recorded import, not vendored | [schemas/core.yaml](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/schemas/core.yaml) |
| `../schemas/shared.yaml` | recorded import, not vendored | [schemas/shared.yaml](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/schemas/shared.yaml) |
| `../fhgff3.json` | not copied; generated upstream | [fhgff3.json](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/fhgff3.json) |
| `../examples/fhgff3/` | [`../examples/fhgff3/`](../examples/fhgff3/) | [examples/fhgff3/](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/tree/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/examples/fhgff3) |
| `../conformance/README.md` | [`../conformance/README.md`](../conformance/README.md) | [conformance/README.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/conformance/README.md) |
| `SCHEMA-VERSIONS.md` | not present locally | [SCHEMA-VERSIONS.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/docs/SCHEMA-VERSIONS.md) |
| `FORMAT.md` | not present locally | [FORMAT.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/docs/FORMAT.md) |
| `../specs/007-gff3-header/plan.md` | not present locally | [plan.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/bdcaecf759b5b2be5fd61bf8f39368a7e3963315/specs/007-gff3-header/plan.md) |

The header rules also rely on the shared format rules (R1–R12) in the publication
repository's `docs/FORMAT.md`, linked above.

## Navigating this copy locally

- Read the byte-exact contract: [`FHGFF3.md`](FHGFF3.md).
- Model: [`../model/fhgff3_linkml.yml`](../model/fhgff3_linkml.yml).
- Examples: [`../examples/fhgff3/`](../examples/fhgff3/).
- Conformance vectors: [`../conformance/README.md`](../conformance/README.md).
- Pinned provenance and update steps: [`../PROVENANCE.md`](../PROVENANCE.md).
- Header tree overview: [`../README.md`](../README.md).
