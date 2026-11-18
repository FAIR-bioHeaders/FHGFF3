# Changelog

## Unreleased

- **HTML binding brought up to the v0.6.0 pin.** The test-only microdata reader
  now carries every released FHGFF3 contract: v0.4.0 to v0.4.2 (`"1.0"`), v0.5.0
  (`"1.1"`) and v0.6.0 (`"1.2"`), with byte copies of the released schemas under
  `tests/fixtures/releases/` and their digests asserted. Writing then reading the
  shared v0.6.0 example `header/examples/fhgff3/minimal-reference.fhgff3.json`
  previously failed with "unsupported FHGFF3 schema release: v0.6.0"; it now
  round-trips. `docs/FHGFF3-MICRODATA.md` names the three contract versions and
  adopts shared rule M5: the writer leaves top-level `x-` extension fields out and
  reports them, and the reader rejects an `x-` itemprop. The test validator learned
  `patternProperties` and `propertyNames`, with ECMA-262 end anchoring. No schema,
  header copy or released byte changes.
- **Binding status made consistent.** The document said both that the shared
  publication step was complete and that website export awaited publication. It
  now separates the completed shared documentation step from the outstanding
  joint-maintainer adoption and binding release. The toolkit runtime is dated to
  its first release: fair-bioheaders 0.10.0 (2026-11-12) already read and wrote
  FHGFF3 microdata with `ExperimentalMicrodataWarning`; 0.11.0 and 0.12.0 keep it.
- **Header parity checks the pin, not only the bytes.** `source.ref` must be a
  release tag (`vX.Y.Z`); with an upstream checkout the tag must resolve to
  `source.commit` (FAIR-bioHeaders-Specification#241). Every file under `header/`
  is now covered, not only the copied directories. CI checks out the pinned tag and
  runs weekly on a schedule.
- **Guidance.** AGENTS.md lists the checks that exist in this repository and ports
  two shared-guidance changes from FAIR-bioHeaders-Specification: the
  "where to look" form of the FHGM real-data paragraph (`e11a9bf`, #245) and the
  FHP absolute-links sentence (`659115c`, #233). `header/docs/README.md` cites
  R1–R15, the range at the pinned v0.6.0 release. `ci/README.md` records the
  0.11.0 toolkit baseline that CI actually installs.

- Correct the binding's runtime handoff: fair-bioheaders 0.11.0 already reads
  and writes FHGFF3 microdata with an experimental-binding warning. Preserve
  the separate binding-publication and website-enablement gates (Tools#140).

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
  The runtime reader and writer were subsequently implemented in
  [FAIR-bioHeaders-Tools#139](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools/pull/139)
  and are available in fair-bioheaders 0.11.0 with an experimental-binding warning;
  the website consumer
  ([fair-bioheaders.github.io#27](https://github.com/FAIR-bioHeaders/fair-bioheaders.github.io/pull/27))
  and family builder (fair-bioheaders.github.io#15) are coordinated, not shipped, and
  website microdata export remains gated. It is enabled only after this binding
  is published and the reader/writer round-trip tests pass.

  `.gitignore` no longer hides the hand-written binding document (`docs/*md` still
  ignores the generated docs). The inherited feature-model tree
  (`src/`, `jsonschema/`, `python/`, `rdf/`, `owl/`, `shex/`, `graphql/`, `csv/`) is
  unchanged.
