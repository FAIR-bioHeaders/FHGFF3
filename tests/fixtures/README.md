# Test fixtures

`fhgff3.json` is a byte-for-byte copy of the released FHGFF3 JSON Schema
(`schemaVersion` `"1.0"`, `$id`
`https://raw.githubusercontent.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/main/fhgff3.json`)
from FAIR-bioHeaders-Specification v0.4.0. It is used **only** by
`tests/test_fhgff3_microdata.py`, through the test-only validator in
`tests/mini_jsonschema.py`, to check that extracted microdata matches the
released contract without a `jsonschema` dependency.

It is not a runtime schema and is not a second source of truth: the published
schema in FAIR-bioHeaders-Specification is authoritative. When the shared schema
changes, refresh this copy in the same change and rerun the tests.
