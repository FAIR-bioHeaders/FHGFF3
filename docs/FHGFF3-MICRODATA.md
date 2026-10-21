# FHGFF3 HTML microdata (draft binding)

**Status: draft proposal, not released.** This document defines the type-specific
FHGFF3 binding for HTML microdata. It is developed in FHGFF3 (issue #5) and must be
published through
[FAIR-bioHeaders-Specification](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification)
before it is adopted. No FHGFF3 release, tag or DOI is created here. The toolkit reader
and writer are **not** shipped in this repository; they remain toolkit work
([FAIR-bioHeaders-Tools#58](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools/issues/58)).
The website consumer
([fair-bioheaders.github.io#27](https://github.com/FAIR-bioHeaders/fair-bioheaders.github.io/pull/27))
is coordinated with this binding and is not updated by it: the annotation HTML added by
that PR deliberately carries no microdata until this contract is published and the
toolkit reader exists. Its readable annotation tables stay consistent with any embedded
metadata they describe.

This binding **reuses** the family rules in
[MICRODATA.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/main/docs/MICRODATA.md)
and
[FORMAT.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/main/docs/FORMAT.md)
R7 and R9. It does not restate or change them; it records only how FHGFF3 differs from
FHR. Where this page and the shared rules could be read differently, the shared rules
win.

> This file is hand-written and is **not** part of the inherited biodatamodels/gff-schema
> generated documentation. In this tree `make clean` removes `docs/`; if the generated
> tree is ever rebuilt, restore this file from Git. The inherited feature-model sources
> (`src/`, `jsonschema/`, `python/`, `rdf/`, `owl/`, `shex/`, `graphql/`, `csv/`) are not
> the FHGFF3 FAIR header and are not touched by this binding.

## Record scope and itemtype

- [H1] A document holds exactly one FHGFF3 item scope: an element with `itemscope` whose
  `itemtype` tokens include the **raw-main FHGFF3 schema URL**
  `https://raw.githubusercontent.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/main/fhgff3.json`.
  The pre-rename URL
  `https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/fhgff3.json`
  is the same file and the same item type. This is rule M1 with the FHGFF3 URL: a
  document with no FHGFF3 scope, or with more than one, is invalid.
- An element with the **FHR** `itemtype` (`…/fhr.json`) is not an FHGFF3 record, even
  when its properties look annotation-specific. FHGFF3 is never identified by the FHR
  itemtype, and an FHGFF3 file is never validated against `fhr.json`
  ([FHGFF3.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/main/docs/FHGFF3.md) G3).
- The `itemtype` is the raw-main URL, exactly as
  [SCHEMA-VERSIONS.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/main/docs/SCHEMA-VERSIONS.md)
  fixes it for microdata. The record's own `schema` property carries the URL that selects
  the contract version (H2).
- FHGFF3 requiredness is the FHGFF3 contract, not FHR's: `annotation` and the genome
  link are required in addition to the shared core fields; genome-only FHR fields
  (`genome`, `assemblyAuthor`, `masking`, `vitalStats`, `assemblySoftware` and the others)
  and FHP-only fields are not FHGFF3 properties at all, so an FHGFF3 scope that carries
  them fails validation.

## Schema selection and unsupported versions

- [H2] The `schema` property selects the contract version, by the fixed-version rules V1
  to V4 of
  [SCHEMA-VERSIONS.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/main/docs/SCHEMA-VERSIONS.md):
  a raw-main URL selects the reader's current FHGFF3 schema; a raw release-tag URL
  (`…/vX.Y.Z/fhgff3.json`) or its w3id form
  (`https://w3id.org/fair-bioheaders/fhgff3/vX.Y.Z`) selects that release's schema.
  Matching is exact, and both repository names are recognised.
- A `schema` value that is not an FHGFF3 schema URL, a release the reader does not have,
  or a `schemaVersion` the selected schema does not accept is **unsupported-version**.
  The document is rejected; it is not checked against another schema, and it is never
  silently treated as FHR. The released FHGFF3 contract is `schemaVersion` `"1.0"`, a
  quoted string; a reader uses the selected schema's own `schemaVersion` rule, and a
  writer copies the value the record already has.
- The `schema` and `schemaVersion` properties are ordinary properties; they are the same
  values the YAML, JSON and GFF3 header forms carry.

## Property bindings

Every FHGFF3 field is bound the same way as in the family rules: `itemprop` names the
field, nested objects introduce an item scope, arrays use a typed container whose
children are `itemprop="item"`, and typed scalars carry `data-fhr-type`. The table gives
the FHGFF3 shape; the shared rules (M1 to M4, R7, R9) apply unchanged.

| Field | JSON type | Microdata shape | Notes |
| --- | --- | --- | --- |
| `schema` | string | string | An FHGFF3 schema URL; selects the version (H2). |
| `schemaVersion` | string `"1.0"` | typed scalar | The value the selected schema accepts. |
| `annotation` | string | string | Required. The annotation's name. |
| `taxon` | object | one item scope | `name` and `uri` strings. |
| `version` | string | string | The annotation's own version. |
| `metadataAuthor` | array of object | array container | Ordered; each item is an `Author` object (H3). |
| `dateCreated` | date string | string | |
| the genome link | object or array | see H4 | At least one of `genomeReference` or an `annotates` `derivedFrom` item. |
| `genomeReference` | object | one item scope | Asserted accession/SeqCol identity; `accession` and `seqcol_id` required, `assemblyName` optional (H4). |
| `derivedFrom` | array of object | array container | Parent FAIR-bioHeaders files by checksum; nested `accessionID` (H3, H4). |
| `source` | array of object | array container | Asserted non-FAIR sources; `name` required (H3). |
| `annotationSoftware` | array of object | array container | Structured software (H3). |
| `annotationProtocol` | uri string | string | |
| `soVersion` | string | string | The Sequence Ontology release used for feature types. |
| `featureCounts` | array of object | array container | `{featureType, count}`; producer assertions (H5). |
| `completeness` | object | one item scope | Single BUSCO object, not an array (H5). |
| `voucherSpecimen` | string | string | |
| `accessionID` | object | one item scope | `name` and `url` strings. |
| `scholarlyArticle` | string | string | DOI. |
| `documentation` | string | string | |
| `identifier` | array of string | array container | |
| `relatedLink` | array of uri strings | array container | |
| `funding` | string | string | |
| `reuseConditions` | string | string | |
| `checksum` | string | string | An ordinary metadata value; see "Validity and verification". |

The optional core fields keep their FHR meaning. Genome-only FHR fields are absent by
construction.

## Nested objects and ordered arrays

- [H3] `metadataAuthor` is an **ordered array** of `Author` objects. Order is preserved.
  A single author is still a one-item array, never a bare object. Each item is a nested
  item scope (`data-fhr-type="object"`); the released core adds the optional `nameType`
  property to `Author`, read as an ordinary property when the selected schema defines it.
- `source`, `derivedFrom`, `annotationSoftware` and `featureCounts` are arrays of
  independent nested objects. Each item is its own item scope; order is preserved; a
  single item is still a one-item array; an empty array is written as an empty array
  container and is distinct from an omitted property. A `derivedFrom` item's `accessionID`
  is a further nested item scope.
- `source` describes an asserted origin and `derivedFrom` a parent **file** identified by
  its FHR-family checksum; they are not interchangeable, and a `source` is never verified
  by checksum.
- `annotationSoftware` items are `Software` objects: `name` (required), optional `version`
  and `uri`, and optional `commandLineOption`, an **ordered array of strings**.
  Command-line strings are data and are never executed; they may contain shell or markup
  characters, which are escaped in the HTML (H6).

## The genome link: asserted identity and checksum parent

- [H4] The FHGFF3 genome link carries the schema's `anyOf` requirement: a record is valid
  only when it has a complete `genomeReference` object **or** a `derivedFrom` item with
  `relationship: annotates`. It may have both; the checksum link is then authoritative.
- **Asserted identity** (`genomeReference`): `accession` (with its version, as published)
  and `seqcol_id` (the GA4GH sequence collection digest the producer supplied) are
  required; `assemblyName` is optional. This is a producer assertion. It is **not** a
  checksum, and `seqcol_id` is **not** a file checksum: it identifies a sequence
  collection through a separate algorithm. Tools never compute or verify it against a
  local genome.
- **Checksum-linked parent** (`derivedFrom`): each item has `headerType`, `checksum` and
  `relationship`, with optional `accessionID` and `seqcol_id`. At most one item may have
  `relationship: annotates`, and such an item must name an **FHR** parent
  (`headerType: FHR`). Further parents with other relationships (for example
  `filteredFrom`) may be listed and may have another header type.
- The two forms are bound separately: the asserted accession/SeqCol object and the
  checksum-linked FHR parent are distinct properties, and a reader must not merge them or
  substitute one for the other. Feature-count or completeness values never stand in for
  the genome link.

## Feature counts and completeness

- [H5] `featureCounts` is an ordered array of `{featureType, count}` objects, where
  `featureType` is the column-3 type as written (`gene`, `mRNA`, `SO:0000704`) and `count`
  is a nonnegative integer. These are **producer assertions about the file, not GFF3
  validation results**. A zero count is a value and is kept (H6). The FHGFF3 header never
  makes the features valid; validating the features themselves is the job of the
  [gff3-validator](https://github.com/FAIR-bioHeaders/gff3-validator), which reports
  header and feature results separately.
- `completeness` is a **single** BUSCO object, one item scope, not an array. It carries
  `lineageDataset` and the counts `completeSingle`, `completeDuplicated`, `fragmented`,
  `missing` and `total`, with optional `buscoVersion` and `mode`. Repeating it is invalid.
  The schema's own requiredness and ranges apply.

## Zero, false, absence and escaping

- [H6] A property that is present with the value `0` is a value, and is kept. It is not
  the same as an omitted property, and a reader must not drop it or rewrite it as absent.
  The same holds for an empty array: `identifier: []` is present.
- FHGFF3 `schemaVersion` `"1.0"` defines no boolean property. If one is added, `false` is
  a value and `data-fhr-type="boolean"` keeps it; absence is omission only.
- Text and attribute values are escaped and decoded once, exactly as M2 and M3 require.
  Unicode, whitespace and character references round-trip unchanged. `data-fhr-type`
  keeps a number-like string a string, and keeps a typed `integer`, `number`, `boolean` or
  `null` exact.
- Script content and event-handler attributes are inert data: a reader never executes
  them and never takes metadata from them. A document whose metadata exists only inside a
  `<script>` block, a handler or another non-rendered place is not valid FHGFF3
  microdata. Publishing or copying a page through another tool is not evidence that its
  microdata survives.

## Repeated properties

- [H7] Repeating a property is read as a list, following M4. A repeated field that takes a
  single value (`annotation`, `schemaVersion`, `taxon`, `genomeReference`, `completeness`,
  `checksum` and the other scalars and single objects) is therefore invalid, and so is a
  repeated array container. The extracted metadata must validate against the selected
  FHGFF3 schema.

## The readable table

- [H8] A standalone FHGFF3 page may include a human-readable table summarising the same
  metadata. The table is a presentation aid: it adds no metadata and is never read back as
  metadata. Every value it shows must equal the corresponding value in the embedded
  microdata, and it must not present an asserted accession/SeqCol identity or a producer
  feature count as a verified result. Tests compare the table rows with the extracted
  record so the two cannot drift apart.

## Validity and verification

Reading and validating FHGFF3 microdata establishes **structural and schema validity
only**: the document has one FHGFF3 item scope, its values follow the binding, and the
extracted metadata matches the selected FHGFF3 schema. It does not establish that the
metadata belongs to any particular GFF3 file, that the genome link is correct, or that the
annotation's features are valid.

In HTML the `checksum` property is an ordinary metadata value. HTML has no
checksum-coverage rule (the checksum rules R1 to R10 cover the FASTA/GFA/GFF3 containers),
so reading or validating microdata does **not** recompute or verify a SHA-512/256 over the
GFF3 bytes. Exporting or copying metadata alone is not verification. File-backed checks
remain separate toolkit actions
([FHGFF3.md](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/main/docs/FHGFF3.md)):

- `bioheaders verify` recomputes the SHA-512/256 over the GFF3 file's exact bytes
  (including any embedded `##FASTA` section) and compares it with the recorded `checksum`.
- `bioheaders verify-links` compares each `derivedFrom` parent checksum with the parent
  file on disk and reports, per parent, `matched`, `not matched` or `not checked`. A match
  establishes file identity, not that the annotation is correct.
- A `genomeReference`, a `source` entry and any `assemblyAccession` a source states cannot
  be verified this way at all; they stay assertions. A supplied SeqCol digest identifies a
  collection through a separate algorithm and is never computed by the tools.

## Examples and tests

The binding is exercised by standalone HTML examples paired with their canonical records,
and by a test-only reader and writer:

| HTML | Canonical record |
| --- | --- |
| [`examples/fhgff3/minimal-reference.microdata.fhgff3.html`](../examples/fhgff3/minimal-reference.microdata.fhgff3.html) | [`minimal-reference.microdata.fhgff3.json`](../examples/fhgff3/minimal-reference.microdata.fhgff3.json) |
| [`examples/fhgff3/minimal-parent.microdata.fhgff3.html`](../examples/fhgff3/minimal-parent.microdata.fhgff3.html) | [`minimal-parent.microdata.fhgff3.json`](../examples/fhgff3/minimal-parent.microdata.fhgff3.json) |
| [`examples/fhgff3/rich-microdata.microdata.fhgff3.html`](../examples/fhgff3/rich-microdata.microdata.fhgff3.html) | [`rich-microdata.microdata.fhgff3.json`](../examples/fhgff3/rich-microdata.microdata.fhgff3.json) |

Each record is also committed as YAML (the same values, checked against the JSON). The
minimal records exercise the two genome-link alternatives separately: `minimal-reference`
has only the asserted accession/SeqCol object, and `minimal-parent` has only the
checksum-linked FHR parent. The rich record has both, plus nested `source`, `derivedFrom`
(with a nested `accessionID`), ordered author and software arrays, `featureCounts` with a
zero count, `completeness`, and escaped Unicode and markup.

Negative fixtures under `examples/fhgff3/` cover the wrong itemtype, an unsupported
version, malformed nesting, a repeated scalar, script-only content, a missing genome link,
two `annotates` relationships and an `annotates` item that is not an FHR parent. All
values are clearly synthetic placeholders; no real accession, DOI, SeqCol digest or author
is invented.

`tests/fhgff3_microdata.py` is a **test-only** reader, writer and table helper built on the
standard library `html.parser`; `tests/mini_jsonschema.py` is a test-only subset validator
so the tests can check the extracted metadata against the released `fhgff3.json` without a
`jsonschema` dependency. Neither is shipped and neither is a runtime parser.
`tests/test_fhgff3_microdata.py` checks that the fixtures extract back to their canonical
records, that the writer reproduces the committed HTML and the canonical JSON/YAML, that
the readable table matches the embedded metadata, and that the negative fixtures are
rejected. `tests/fixtures/fhgff3.json` is a copy of the released shared schema used only by
these tests.

The rule ids H1 to H8 are stable labels local to this document. They add no requirements
beyond the text above and are not part of the shared conformance manifest, which covers
the R, M, J, P and G rules.

## What remains outside this document

- **Toolkit reader and writer**: FAIR-bioHeaders-Tools#58. FHGFF3 HTML microdata output
  is still unsupported until that work lands.
- **Website binding**: fair-bioheaders.github.io#27, with the family builder in
  fair-bioheaders.github.io#15. The annotation forms and readable tables added by website
  PR #27 stay microdata-free until this contract is published and the toolkit reader
  exists. Website microdata export is enabled only after the binding and the reader/writer
  round-trip tests pass.
- **Publication**: this draft must be reviewed and published through
  FAIR-bioHeaders-Specification before any of the above treats it as adopted.
