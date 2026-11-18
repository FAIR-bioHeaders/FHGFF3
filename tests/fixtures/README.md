# Test fixtures

`releases/fhgff3-v0.4.0.json`, `releases/fhgff3-v0.5.0.json` and
`releases/fhgff3-v0.6.0.json` are byte-for-byte copies of `fhgff3.json` at the
FAIR-bioHeaders-Specification `v0.4.0`, `v0.5.0` and `v0.6.0` tags (FHGFF3
`schemaVersion` `"1.0"`, `"1.1"` and `"1.2"`; every copy has `$id`
`https://raw.githubusercontent.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/main/fhgff3.json`).
`tests/test_fhgff3_microdata.py` asserts their SHA-256 digests. They are used **only** by
`tests/test_fhgff3_microdata.py`, through the test-only validator in
`tests/mini_jsonschema.py`, to check that extracted microdata matches the
released contract without a `jsonschema` dependency.

`tests/fhgff3_microdata.py` maps the fixed releases it carries to these copies
(`SUPPORTED_RELEASES`): v0.4.0, v0.4.1 and v0.4.2 publish the same FHGFF3 `"1.0"`
schema bytes, so all three map to `fhgff3-v0.4.0.json`; v0.5.0 and v0.6.0 map to
their own copies. An unknown release is rejected
rather than checked against one of these local copies.

It is not a runtime schema and is not a second source of truth: the published
schema in FAIR-bioHeaders-Specification is authoritative. When the shared schema
releases a new FHGFF3 contract, add its copy, its digest and its release-map entry
in the same change and rerun the tests.
