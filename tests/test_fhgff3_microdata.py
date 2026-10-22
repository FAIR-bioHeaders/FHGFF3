# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The draft FHGFF3 HTML microdata binding (docs/FHGFF3-MICRODATA.md).

The reader and writer live in ``tests/fhgff3_microdata.py`` and the small
schema validator in ``tests/mini_jsonschema.py``: both are test-only. The
runtime reader and writer remain toolkit work (FAIR-bioHeaders-Tools#58), and
the website consumer (fair-bioheaders.github.io#27) and family builder
(fair-bioheaders.github.io#15) are coordinated, not shipped here. The vendored
``tests/fixtures/fhgff3.json`` is a copy of the released shared schema, used
only so the tests can say the extracted metadata validates against it.
"""

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import fhgff3_microdata  # noqa: E402
import mini_jsonschema  # noqa: E402

FHGFF3_ITEMTYPE = fhgff3_microdata.FHGFF3_ITEMTYPE
FHR_ITEMTYPE = (
    "https://raw.githubusercontent.com/FAIR-bioHeaders/"
    "FAIR-bioHeaders-Specification/main/fhr.json"
)
EXAMPLES = ROOT / "examples" / "fhgff3"
DOC = ROOT / "docs" / "FHGFF3-MICRODATA.md"
SCHEMA = json.loads(
    (ROOT / "tests" / "fixtures" / "releases" / "fhgff3-v0.4.0.json")
    .read_text(encoding="utf-8"))

RELEASE_040 = (
    "https://raw.githubusercontent.com/FAIR-bioHeaders/"
    "FAIR-bioHeaders-Specification/v0.4.0/fhgff3.json"
)
RELEASE_040_W3ID = "https://w3id.org/fair-bioheaders/fhgff3/v0.4.0"
RELEASE_041 = (
    "https://raw.githubusercontent.com/FAIR-bioHeaders/"
    "FAIR-bioHeaders-Specification/v0.4.1/fhgff3.json"
)
CHECKSUM = "A" * 43 + "="

# The committed valid HTML fixtures and the canonical record each one pins.
VALID_FIXTURES = {
    "minimal-reference.microdata.fhgff3.html": "minimal-reference.microdata.fhgff3.json",
    "minimal-parent.microdata.fhgff3.html": "minimal-parent.microdata.fhgff3.json",
    "rich-microdata.microdata.fhgff3.html": "rich-microdata.microdata.fhgff3.json",
}
NEGATIVE_FIXTURES = [
    "invalid-itemtype.microdata.fhgff3.html",
    "invalid-unsupported-version.microdata.fhgff3.html",
    "invalid-unknown-release.microdata.fhgff3.html",
    "invalid-malformed-nesting.microdata.fhgff3.html",
    "invalid-repeated-scalar.microdata.fhgff3.html",
    "invalid-repeated-array.microdata.fhgff3.html",
    "invalid-unsafe-content.microdata.fhgff3.html",
    "invalid-no-genome-link.microdata.fhgff3.html",
    "invalid-two-annotates.microdata.fhgff3.html",
    "invalid-annotates-non-fhr.microdata.fhgff3.html",
]


def load_record(name):
    text = (EXAMPLES / name).read_text(encoding="utf-8")
    return json.loads(text) if name.endswith(".json") else None


def same_json(left, right):
    """JSON equality that keeps booleans, numbers, strings and containers apart."""
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(same_json(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(map(same_json, left, right))
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    return type(left) is type(right) and left == right


def read_fixture(name):
    """Extract a fixture without validating it against the schema."""
    return fhgff3_microdata.read_page(
        (EXAMPLES / name).read_text(encoding="utf-8"), SCHEMA)


def extract_page(page):
    """Read a document and reject it unless it matches the selected schema (M4)."""
    record = fhgff3_microdata.read_page(page, SCHEMA)
    schema = fhgff3_microdata.resolve_schema(record["schema"], SCHEMA)
    mini_jsonschema.validate(record, schema)
    return record


def extract(name):
    """Read a fixture and reject it unless it also matches fhgff3.json (M4)."""
    return extract_page((EXAMPLES / name).read_text(encoding="utf-8"))


class FHGFF3MicrodataFixtureTests(unittest.TestCase):
    def test_valid_fixtures_extract_to_their_canonical_records(self):
        for html, record_name in VALID_FIXTURES.items():
            with self.subTest(fixture=html):
                expected = load_record(record_name)
                self.assertTrue(same_json(read_fixture(html), expected))
                mini_jsonschema.validate(expected, SCHEMA)

    def test_committed_html_is_the_writer_output(self):
        for html, record_name in VALID_FIXTURES.items():
            with self.subTest(fixture=html):
                expected = fhgff3_microdata.write_page(load_record(record_name))
                self.assertEqual((EXAMPLES / html).read_text(encoding="utf-8"), expected)

    def test_committed_json_and_yaml_match_the_canonical_writers(self):
        for record_name in VALID_FIXTURES.values():
            with self.subTest(record=record_name):
                record = load_record(record_name)
                stem = record_name[: -len(".json")]
                json_text = (EXAMPLES / record_name).read_text(encoding="utf-8")
                yaml_text = (EXAMPLES / f"{stem}.yaml").read_text(encoding="utf-8")
                self.assertEqual(json_text, fhgff3_microdata.to_json(record))
                self.assertEqual(yaml_text, fhgff3_microdata.to_yaml(record))

    def test_negative_fixtures_are_rejected(self):
        for name in NEGATIVE_FIXTURES:
            with self.subTest(fixture=name):
                with self.assertRaises(
                        (fhgff3_microdata.MicrodataError,
                         mini_jsonschema.ValidationError)):
                    extract(name)

    def test_readable_table_matches_the_embedded_metadata(self):
        for html, record_name in VALID_FIXTURES.items():
            with self.subTest(fixture=html):
                record = load_record(record_name)
                rows = fhgff3_microdata.read_table(
                    (EXAMPLES / html).read_text(encoding="utf-8"))
                self.assertEqual(rows, fhgff3_microdata.table_rows(record))
                self.assertTrue(rows)

    def test_script_content_in_a_fixture_is_escaped_in_the_html(self):
        page = (EXAMPLES / "rich-microdata.microdata.fhgff3.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)


class FHGFF3MicrodataBindingTests(unittest.TestCase):
    def minimal(self):
        return load_record("minimal-reference.microdata.fhgff3.json")

    def rich(self):
        return load_record("rich-microdata.microdata.fhgff3.json")

    def test_record_scope_uses_the_fhgff3_itemtype(self):
        page = fhgff3_microdata.write_page(self.minimal())
        self.assertIn(f'itemtype="{FHGFF3_ITEMTYPE}"', page)
        self.assertNotIn(FHR_ITEMTYPE, page)
        # The itemtype is the raw-main FHGFF3 schema URL, distinct from the
        # versioned `schema` value the record itself carries.
        self.assertNotEqual(FHGFF3_ITEMTYPE, self.minimal()["schema"])

    def test_fhr_itemtype_is_not_an_fhgff3_document(self):
        page = fhgff3_microdata.write_page(self.minimal(), itemtype=FHR_ITEMTYPE)
        with self.assertRaises(fhgff3_microdata.MicrodataError):
            fhgff3_microdata.read_page(page, SCHEMA)

    def test_two_fhgff3_scopes_are_rejected(self):
        page = fhgff3_microdata.write_page(self.minimal())
        scope = page[page.index("<div "):page.index("</div>") + len("</div>")]
        page = page.replace("</body>", scope + "</body>", 1)
        with self.assertRaises(fhgff3_microdata.MicrodataError):
            fhgff3_microdata.read_page(page, SCHEMA)

    def test_schema_property_selects_an_fhgff3_contract(self):
        for selected in (
            RELEASE_040,
            RELEASE_040_W3ID,
            RELEASE_041,
            "https://raw.githubusercontent.com/FAIR-bioHeaders/"
            "FHR-Specification/v0.4.0/fhgff3.json",
        ):
            with self.subTest(schema=selected):
                record = dict(self.minimal(), schema=selected)
                self.assertTrue(same_json(
                    extract_page(fhgff3_microdata.write_page(record)), record))

    def test_unavailable_release_is_rejected(self):
        # V4: an unknown release is unsupported-version; the reader must not
        # fall back to its local v0.4.0 copy.
        for selected in (
            "https://raw.githubusercontent.com/FAIR-bioHeaders/"
            "FAIR-bioHeaders-Specification/v9.9.9/fhgff3.json",
            "https://w3id.org/fair-bioheaders/fhgff3/v9.9.9",
        ):
            with self.subTest(schema=selected):
                record = dict(self.minimal(), schema=selected)
                with self.assertRaises(fhgff3_microdata.MicrodataError):
                    fhgff3_microdata.read_page(
                        fhgff3_microdata.write_page(record), SCHEMA)

    def test_an_fhr_schema_value_is_not_an_fhgff3_record(self):
        record = dict(self.minimal(), schema=FHR_ITEMTYPE)
        with self.assertRaises(fhgff3_microdata.MicrodataError):
            fhgff3_microdata.read_page(fhgff3_microdata.write_page(record), SCHEMA)

    def test_a_non_release_ref_is_unsupported(self):
        # V4: a raw URL naming any ref other than main or a release tag is
        # unsupported-version, not a fallback to another schema.
        record = dict(self.minimal(),
                      schema="https://raw.githubusercontent.com/FAIR-bioHeaders/"
                             "FAIR-bioHeaders-Specification/0123abc/fhgff3.json")
        with self.assertRaises(fhgff3_microdata.MicrodataError):
            fhgff3_microdata.read_page(fhgff3_microdata.write_page(record), SCHEMA)

    def test_unsupported_version_is_rejected(self):
        record = dict(self.minimal(), schemaVersion="2.0")
        page = fhgff3_microdata.write_page(record)
        # The reader selects the released contract and refuses the version
        # instead of silently checking another schema.
        with self.assertRaises(fhgff3_microdata.MicrodataError):
            fhgff3_microdata.read_page(page, SCHEMA)
        # The released schema's own enum rejects it too.
        self.assertTrue(list(mini_jsonschema.iter_errors(record, SCHEMA)))

    def test_repeated_scalar_property_becomes_a_list(self):
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            "</div>",
            '<span itemprop="annotation" data-fhr-type="string">Second</span></div>', 1)
        extracted = fhgff3_microdata.read_page(page, SCHEMA)
        self.assertEqual(extracted["annotation"],
                         [self.minimal()["annotation"], "Second"])
        self.assertTrue(list(mini_jsonschema.iter_errors(extracted, SCHEMA)))

    def test_repeated_array_containers_are_not_flattened(self):
        # H7: two array containers are two repeated containers, not one flat
        # list. They stay nested so schema validation rejects the record.
        container = ('<span itemprop="metadataAuthor" data-fhr-type="array">'
                     '<span itemprop="item" itemscope data-fhr-type="object">'
                     '<span itemprop="name" data-fhr-type="string">Synthetic '
                     "metadata author (placeholder)</span></span></span>")
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            container, container + container, 1)
        extracted = fhgff3_microdata.read_page(page, SCHEMA)
        self.assertEqual(len(extracted["metadataAuthor"]), 2)
        self.assertTrue(all(isinstance(item, list)
                            for item in extracted["metadataAuthor"]))
        with self.assertRaises(mini_jsonschema.ValidationError):
            extract_page(page)

    def test_ordinary_repeated_array_properties_form_a_flat_list(self):
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            "</div>", '<span itemprop="identifier">ex:one</span>'
            '<span itemprop="identifier">ex:two</span></div>', 1)
        extracted = extract_page(page)
        self.assertEqual(extracted["identifier"], ["ex:one", "ex:two"])

    def test_malformed_array_child_is_rejected(self):
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            'itemprop="item" itemscope', 'itemprop="author" itemscope', 1)
        with self.assertRaises(fhgff3_microdata.MicrodataError):
            fhgff3_microdata.read_page(page, SCHEMA)

    def test_object_without_itemscope_is_rejected(self):
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            '<span itemprop="genomeReference" itemscope',
            '<span itemprop="genomeReference"', 1)
        with self.assertRaises(fhgff3_microdata.MicrodataError):
            fhgff3_microdata.read_page(page, SCHEMA)

    def test_nested_unrelated_scope_does_not_leak_properties(self):
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            "</div>",
            '<div itemscope><span itemprop="annotation">Leaked</span></div></div>', 1)
        self.assertTrue(same_json(
            fhgff3_microdata.read_page(page, SCHEMA), self.minimal()))

    def test_zero_is_a_value_and_absence_is_omission(self):
        rich = read_fixture("rich-microdata.microdata.fhgff3.html")
        self.assertEqual(rich["featureCounts"][2]["count"], 0)
        self.assertIn("featureCounts", rich)
        self.assertNotIn("featureCounts", self.minimal())
        # An empty array is present and distinct from an omitted list.
        record = dict(self.minimal(), identifier=[])
        self.assertTrue(same_json(
            fhgff3_microdata.read_page(
                fhgff3_microdata.write_page(record), SCHEMA), record))

    def test_false_is_a_value_not_absence(self):
        # FHGFF3 schemaVersion 1.0 defines no boolean property; the typed form
        # keeps a false value when one is added. The reader must not drop it.
        self.assertIs(fhgff3_microdata._parse_typed("false", "boolean"), False)
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            "</div>",
            '<span itemprop="newFlag" data-fhr-type="boolean">false</span></div>', 1)
        extracted = fhgff3_microdata.read_page(page, SCHEMA)
        self.assertIs(extracted["newFlag"], False)

    def test_ordered_arrays_keep_their_order(self):
        rich = read_fixture("rich-microdata.microdata.fhgff3.html")
        self.assertEqual([author["name"] for author in rich["metadataAuthor"]],
                         ["Synthetic first author (placeholder)",
                          "Synthetic second author (placeholder)"])
        self.assertEqual(rich["annotationSoftware"][0]["commandLineOption"],
                         ["--species", "human", "--flag=<script>"])
        self.assertEqual([count["featureType"] for count in rich["featureCounts"]],
                         ["gene", "mRNA", "exon"])
        self.assertEqual([parent["headerType"] for parent in rich["derivedFrom"]],
                         ["FHR", "FHGFF3"])

    def test_nested_sources_parents_and_counts(self):
        rich = read_fixture("rich-microdata.microdata.fhgff3.html")
        self.assertEqual(rich["derivedFrom"][1]["accessionID"],
                         {"name": "Synthetic source annotation (placeholder)"})
        self.assertEqual(rich["source"][0]["name"],
                         "Synthetic evidence set (placeholder)")
        self.assertEqual(rich["source"][0]["sequenceCount"], 0)
        self.assertEqual(rich["completeness"]["completeDuplicated"], 0)
        self.assertEqual(rich["genomeReference"],
                         {"accession": "SYNTHETIC_ASSEMBLY.1",
                          "seqcol_id": "S" * 32,
                          "assemblyName": "SyntheticAssembly1"})

    def test_asserted_genome_and_checksum_parent_stay_separate(self):
        rich = read_fixture("rich-microdata.microdata.fhgff3.html")
        # The asserted identity is the accession/SeqCol object; the verifiable
        # parent is a checksum-linked FHR derivedFrom item. They are distinct.
        self.assertEqual(rich["genomeReference"]["accession"], "SYNTHETIC_ASSEMBLY.1")
        annotates = [p for p in rich["derivedFrom"] if p["relationship"] == "annotates"]
        self.assertEqual(len(annotates), 1)
        self.assertEqual(annotates[0]["headerType"], "FHR")
        self.assertNotEqual(annotates[0]["checksum"],
                            rich["genomeReference"]["seqcol_id"])
        reference_only = load_record("minimal-reference.microdata.fhgff3.json")
        self.assertIn("genomeReference", reference_only)
        self.assertNotIn("derivedFrom", reference_only)
        parent_only = load_record("minimal-parent.microdata.fhgff3.json")
        self.assertNotIn("genomeReference", parent_only)
        self.assertIn("derivedFrom", parent_only)

    def test_genome_link_alternatives_are_enforced(self):
        # anyOf: genomeReference, or an annotates derivedFrom item.
        no_link = dict(self.minimal())
        del no_link["genomeReference"]
        self.assertTrue(list(mini_jsonschema.iter_errors(no_link, SCHEMA)))
        with_reference = dict(no_link, genomeReference={"accession": "SYNTHETIC.1",
                                                       "seqcol_id": "S" * 32})
        mini_jsonschema.validate(with_reference, SCHEMA)
        with_parent = dict(no_link, derivedFrom=[{
            "headerType": "FHR", "checksum": "B" * 43 + "=",
            "relationship": "annotates"}])
        mini_jsonschema.validate(with_parent, SCHEMA)

    def test_at_most_one_annotates_relationship(self):
        record = dict(self.minimal(), derivedFrom=[
            {"headerType": "FHR", "checksum": "B" * 43 + "=", "relationship": "annotates"},
            {"headerType": "FHR", "checksum": "C" * 43 + "=", "relationship": "annotates"},
        ])
        self.assertTrue(list(mini_jsonschema.iter_errors(record, SCHEMA)))

    def test_annotates_relationship_requires_an_fhr_parent(self):
        record = dict(self.minimal(), derivedFrom=[{
            "headerType": "FHGFF3", "checksum": "C" * 43 + "=",
            "relationship": "annotates"}])
        self.assertTrue(list(mini_jsonschema.iter_errors(record, SCHEMA)))

    def test_feature_counts_are_producer_assertions(self):
        # The schema bounds counts only at zero; it does not validate them
        # against any GFF3 feature file (that is the gff3-validator's job).
        record = dict(self.minimal(), featureCounts=[
            {"featureType": "gene", "count": -1}])
        self.assertTrue(list(mini_jsonschema.iter_errors(record, SCHEMA)))
        zero = dict(self.minimal(), featureCounts=[
            {"featureType": "gene", "count": 0}])
        mini_jsonschema.validate(zero, SCHEMA)
        doc = DOC.read_text(encoding="utf-8")
        self.assertIn("producer assertion", doc)

    def test_escaped_unicode_and_markup_round_trip_as_data(self):
        rich = read_fixture("rich-microdata.microdata.fhgff3.html")
        self.assertIn("café", rich["annotation"])
        self.assertIn("<script>alert(1)</script>", rich["documentation"])
        self.assertIn("&", rich["documentation"])
        self.assertIn("測試", rich["documentation"])

    def test_script_and_handler_content_is_never_metadata(self):
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            f'<span itemprop="checksum" data-fhr-type="string">'
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</span>",
            '<script>document.getElementById("x").textContent="A";</script>', 1)
        extracted = fhgff3_microdata.read_page(page, SCHEMA)
        self.assertNotIn("checksum", extracted)
        self.assertTrue(list(mini_jsonschema.iter_errors(extracted, SCHEMA)))
        # A handler attribute is inert: it is not a property and is ignored.
        with_handler = fhgff3_microdata.write_page(self.minimal()).replace(
            "<div itemscope", '<div onclick="run()" itemscope', 1)
        self.assertTrue(same_json(
            fhgff3_microdata.read_page(with_handler, SCHEMA), self.minimal()))

    def test_script_with_itemprop_is_not_a_property(self):
        checksum = ('<span itemprop="checksum" data-fhr-type="string">'
                    f"{CHECKSUM}</span>")
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            checksum,
            '<script itemprop="checksum" data-fhr-type="string">'
            f"{CHECKSUM}</script>", 1)
        extracted = fhgff3_microdata.read_page(page, SCHEMA)
        self.assertNotIn("checksum", extracted)
        with self.assertRaises(mini_jsonschema.ValidationError):
            extract_page(page)
        # A property and its descendants inside a script are still inert.
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            checksum,
            '<script itemprop="voucherSpecimen"><span itemprop="checksum" '
            f'data-fhr-type="string">{CHECKSUM}</span></script>', 1)
        extracted = fhgff3_microdata.read_page(page, SCHEMA)
        self.assertNotIn("checksum", extracted)
        self.assertNotIn("voucherSpecimen", extracted)

    def test_script_text_inside_a_property_is_excluded(self):
        documentation = fhgff3_microdata._write_property(
            "documentation", self.minimal()["documentation"])
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            documentation,
            '<span itemprop="documentation" data-fhr-type="string">'
            "before<script>secret</script>after</span>", 1)
        self.assertEqual(
            fhgff3_microdata.read_page(page, SCHEMA)["documentation"],
            "beforeafter")

    def test_property_inside_ordinary_property_is_read(self):
        documentation = fhgff3_microdata._write_property(
            "documentation", self.minimal()["documentation"])
        checksum = ('<span itemprop="checksum" data-fhr-type="string">'
                    f"{CHECKSUM}</span>")
        page = fhgff3_microdata.write_page(self.minimal()).replace(checksum, "", 1)
        page = page.replace(
            documentation,
            '<span itemprop="documentation" data-fhr-type="string">'
            f"{checksum}</span>", 1)
        extracted = extract_page(page)
        self.assertEqual(extracted["checksum"], CHECKSUM)
        self.assertEqual(extracted["documentation"], CHECKSUM)
        self.assertEqual(extracted, dict(self.minimal(), documentation=CHECKSUM))

    def test_omitted_end_tags_match_explicit_end_tags(self):
        page = fhgff3_microdata.write_page(self.minimal())
        version = ('<span itemprop="version" data-fhr-type="string">'
                   "1.0.0</span>")
        expected_with_conditions = dict(self.minimal(), reuseConditions="CC0-1.0")
        cases = [
            ("p",
             '<p itemprop="version" data-fhr-type="string">1.0.0'
             "<span></span><div></div>",
             '<p itemprop="version" data-fhr-type="string">1.0.0'
             "<span></span></p><div></div>",
             self.minimal()),
            ("li",
             '<ul><li itemprop="version" data-fhr-type="string">1.0.0'
             '<li itemprop="reuseConditions" data-fhr-type="string">CC0-1.0</ul>',
             '<ul><li itemprop="version" data-fhr-type="string">1.0.0</li>'
             '<li itemprop="reuseConditions" data-fhr-type="string">CC0-1.0</li></ul>',
             expected_with_conditions),
            ("dt/dd",
             '<dl><dt itemprop="version" data-fhr-type="string">1.0.0'
             '<dd itemprop="reuseConditions" data-fhr-type="string">CC0-1.0</dl>',
             '<dl><dt itemprop="version" data-fhr-type="string">1.0.0</dt>'
             '<dd itemprop="reuseConditions" data-fhr-type="string">CC0-1.0</dd></dl>',
             expected_with_conditions),
            ("tr",
             '<table><tr><td itemprop="version" data-fhr-type="string">1.0.0'
             '<tr><td itemprop="reuseConditions" data-fhr-type="string">CC0-1.0</table>',
             '<table><tr><td itemprop="version" data-fhr-type="string">1.0.0</td></tr>'
             '<tr><td itemprop="reuseConditions" data-fhr-type="string">CC0-1.0'
             "</td></tr></table>",
             expected_with_conditions),
            ("td",
             '<table><tr><td itemprop="version" data-fhr-type="string">1.0.0'
             '<td itemprop="reuseConditions" data-fhr-type="string">CC0-1.0</table>',
             '<table><tr><td itemprop="version" data-fhr-type="string">1.0.0</td>'
             '<td itemprop="reuseConditions" data-fhr-type="string">CC0-1.0'
             "</td></tr></table>",
             expected_with_conditions),
            ("th",
             '<table><tr><th itemprop="version" data-fhr-type="string">1.0.0'
             '<th itemprop="reuseConditions" data-fhr-type="string">CC0-1.0</table>',
             '<table><tr><th itemprop="version" data-fhr-type="string">1.0.0</th>'
             '<th itemprop="reuseConditions" data-fhr-type="string">CC0-1.0'
             "</th></tr></table>",
             expected_with_conditions),
            ("option",
             '<select><option itemprop="version" data-fhr-type="string">1.0.0'
             '<option itemprop="reuseConditions" data-fhr-type="string">CC0-1.0</select>',
             '<select><option itemprop="version" data-fhr-type="string">1.0.0</option>'
             '<option itemprop="reuseConditions" data-fhr-type="string">CC0-1.0'
             "</option></select>",
             expected_with_conditions),
        ]
        for label, omitted, explicit, expected in cases:
            with self.subTest(tag=label):
                self.assertIn(version, page)
                omitted_page = page.replace(version, omitted, 1)
                explicit_page = page.replace(version, explicit, 1)
                self.assertTrue(same_json(
                    fhgff3_microdata.read_page(omitted_page, SCHEMA), expected))
                self.assertTrue(same_json(
                    fhgff3_microdata.read_page(explicit_page, SCHEMA), expected))

    def test_first_attribute_wins(self):
        page = fhgff3_microdata.write_page(self.minimal()).replace(
            '<span itemprop="annotation" data-fhr-type="string">',
            '<span itemprop="annotation" itemprop="notAField" data-fhr-type="string">', 1)
        extracted = fhgff3_microdata.read_page(page, SCHEMA)
        self.assertNotIn("notAField", extracted)
        self.assertEqual(extracted["annotation"], self.minimal()["annotation"])

    def test_mini_validator_rejects_bad_scalar_types(self):
        self.assertTrue(list(mini_jsonschema.iter_errors(
            dict(self.minimal(), annotation=123), SCHEMA)))
        self.assertTrue(list(mini_jsonschema.iter_errors(
            dict(self.minimal(), featureCounts=[{"featureType": "gene", "count": "2"}]),
            SCHEMA)))


class FHGFF3MicrodataArtifactTests(unittest.TestCase):
    def test_vendored_schema_is_the_released_contract(self):
        self.assertEqual(SCHEMA["$id"], FHGFF3_ITEMTYPE)
        self.assertEqual(SCHEMA["$schema"],
                         "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(SCHEMA["properties"]["schemaVersion"]["enum"], ["1.0"])
        self.assertEqual(SCHEMA["required"][:1], ["schema"])

    def test_binding_document_exists_and_names_the_itemtype(self):
        self.assertTrue(DOC.is_file(), "docs/FHGFF3-MICRODATA.md is missing")
        doc = DOC.read_text(encoding="utf-8")
        self.assertIn(FHGFF3_ITEMTYPE, doc)
        self.assertIn("genomeReference", doc)
        self.assertIn("derivedFrom", doc)
        self.assertIn("featureCounts", doc)
        self.assertIn("annotates", doc)

    def test_yaml_writer_represents_empty_collections(self):
        text = fhgff3_microdata.to_yaml({
            "identifier": [],
            "taxon": {},
            "name": "x",
        })
        self.assertIn("identifier: []", text)
        self.assertIn("taxon: {}", text)
        self.assertNotIn("identifier:\n", text)
        self.assertEqual(
            fhgff3_microdata.to_yaml({"items": [[]], "objects": [{}]}),
            "items:\n  - []\nobjects:\n  - {}\n")

    def test_resolve_schema_maps_releases_to_fixed_contracts(self):
        # The raw-main URL selects the reader's current schema.
        self.assertIs(fhgff3_microdata.resolve_schema(FHGFF3_ITEMTYPE, SCHEMA), SCHEMA)
        for selected in (RELEASE_040, RELEASE_040_W3ID, RELEASE_041):
            with self.subTest(schema=selected):
                resolved = fhgff3_microdata.resolve_schema(selected, SCHEMA)
                self.assertEqual(
                    resolved["properties"]["schemaVersion"]["enum"], ["1.0"])
        for selected in (
            "https://raw.githubusercontent.com/FAIR-bioHeaders/"
            "FAIR-bioHeaders-Specification/v9.9.9/fhgff3.json",
            "https://w3id.org/fair-bioheaders/fhgff3/v9.9.9",
        ):
            with self.subTest(schema=selected):
                with self.assertRaises(fhgff3_microdata.MicrodataError):
                    fhgff3_microdata.resolve_schema(selected, SCHEMA)


if __name__ == "__main__":
    unittest.main()
