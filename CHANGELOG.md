# Changelog

## Unreleased

- **Re-pin `header/` to the shared v0.6.0 release** (FAIR-bioHeaders-Specification
  `0ae18b00ee4bd71ab2dc28bae706b0f9d195076b`, the `v0.6.0` tag commit). The byte copy
  moves from `bdcaecf7` (2026-10-21, pre-v0.5.0): all 39 previously copied files were
  re-extracted from the new pin, 10 `fhgff3` conformance vectors added (3 valid —
  `fhgff3-busco-lineage-dotted`, `fhgff3-extension-fields`,
  `fhgff3-version-3-trailing-whitespace` — and 7 invalid — the R15/J-family extension
  rejections, the G1 `##gff-version` near misses and `fhgff3-busco-lineage-trailing-dot`),
  nothing deleted; `header/provenance.json` now lists 49 copied files with recomputed
  sizes and SHA-256 digests. The recorded imports move `schemas/shared.yaml`
  `0e7e08d5…` → `19afd1d8…` (the #170 dotted-`lineageDataset` widening, FHGFF3 1.2),
  `conformance/manifest.json` and `docs/FORMAT.md` to their v0.6.0 digests;
  `schemas/core.yaml` is unchanged (`2bd657ec…`). Local companion records updated to
  match: `header/PROVENANCE.md` (pin block and 49-row file table),
  `header/docs/README.md` (pinned-commit URLs), `header/conformance/README.md`
  (vector counts 18 valid / 20 invalid and the cited rule census).
  `.github/workflows/header-parity.yml`'s shared-conformance toolkit baseline moves from
  fair-bioheaders 0.8.1 to 0.11.0, the release that bundles v0.6.0: the pinned
  upstream suite fails under 0.8.1 (it predates the v0.5.0 schema citations and the
  G1 grammar enforcement) and passes 291/291 under 0.11.0. No hand-editing of copied
  bytes; no schema-contract change in this repository. Refs FAIR-bioHeaders-Specification#222, #170.

- Add always-reporting owned-documentation lint/local-link checks, scheduled and
  manual external-link checks, manual parity diagnostics and a pinned shared
  conformance job using released fair-bioheaders 0.8.1 (#8). Document why parity
  replaces local schema generation/drift under the adopted mirror layout, while
  inherited-model execution remains disabled pending #3. The parent #2 remains
  open; copied header bytes and released contracts are unchanged.

- **Draft/proposal.** Specify the FHGFF3 HTML microdata binding (FHGFF3#5).
  `docs/FHGFF3-MICRODATA.md` defines the FHGFF3 item scope and itemtype (the raw-main
  `fhgff3.json` URL, never the FHR itemtype), fixed-version schema selection, and a
  binding for every FHGFF3 field on top of the shared rules M1 to M4 and R9 in
  `docs/MICRODATA.md`: nested `genomeReference`, `derivedFrom`, `source`,
  `annotationSoftware`, `featureCounts` and `completeness`; ordered author and software
  arrays; single objects versus repeated scalars; zero and `false` versus absence;
  escaped Unicode and text; and the readable-table consistency rule. It carries through
  the schema's alternative genome-reference requirements (an asserted accession/SeqCol
  object **or** a checksum-linked FHR parent), the at-most-one `annotates` relationship
  and the FHR parent-type restriction, and it states that feature counts are producer
  assertions, not GFF3 validation results. It separates structural/schema validity from
  file-backed checksum and parent verification.

  New standalone examples `examples/fhgff3/minimal-reference.microdata.fhgff3.html`,
  `examples/fhgff3/minimal-parent.microdata.fhgff3.html` and
  `examples/fhgff3/rich-microdata.microdata.fhgff3.html` pair with their canonical
  JSON and YAML records, with negative fixtures for the wrong itemtype, an unsupported
  version, malformed nesting, a repeated scalar, script-only content, a missing genome
  link, two `annotates` relationships and a non-FHR `annotates` parent. A **test-only**
  reader, writer and table helper in `tests/fhgff3_microdata.py` (standard library
  `html.parser`), a test-only schema-subset validator in `tests/mini_jsonschema.py` and
  `tests/test_fhgff3_microdata.py` extract the fixtures back to the canonical records,
  compare the readable table with the embedded metadata and reject the negatives.

  This is a proposal for review and publication through FAIR-bioHeaders-Specification.
  The runtime reader and writer remain toolkit work
  ([FAIR-bioHeaders-Tools#58](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools/issues/58));
  the website consumer
  ([fair-bioheaders.github.io#27](https://github.com/FAIR-bioHeaders/fair-bioheaders.github.io/pull/27))
  and family builder (fair-bioheaders.github.io#15) are coordinated, not shipped, and
  FHGFF3 HTML microdata output is still unsupported. Website microdata export is enabled
  only after this binding and the round-trip tests pass.

  `.gitignore` no longer hides the hand-written binding document (`docs/*md` still
  ignores the generated docs). The inherited feature-model tree
  (`src/`, `jsonschema/`, `python/`, `rdf/`, `owl/`, `shex/`, `graphql/`, `csv/`) is
  unchanged.
