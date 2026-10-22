# Test fixtures

`releases/fhgff3-v0.4.0.json` is a byte-for-byte copy of the released FHGFF3 JSON
Schema (`schemaVersion` `"1.0"`, `$id`
`https://raw.githubusercontent.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/main/fhgff3.json`)
from FAIR-bioHeaders-Specification v0.4.0. It is used **only** by
`tests/test_fhgff3_microdata.py`, through the test-only validator in
`tests/mini_jsonschema.py`, to check that extracted microdata matches the
released contract without a `jsonschema` dependency.

`tests/fhgff3_microdata.py` maps the fixed releases it carries to these copies
(`SUPPORTED_RELEASES`): v0.4.0 and v0.4.1 both publish the same FHGFF3 `"1.0"`
contract, so both map to `fhgff3-v0.4.0.json`. An unknown release is rejected
rather than checked against this local copy.

It is not a runtime schema and is not a second source of truth: the published
schema in FAIR-bioHeaders-Specification is authoritative. When the shared schema
changes, refresh this copy and the release map in the same change and rerun the
tests.
