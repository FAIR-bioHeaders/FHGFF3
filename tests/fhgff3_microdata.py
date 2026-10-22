# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Test-only FHGFF3 HTML microdata reader, writer and table helpers.

Implements the draft binding in ``docs/FHGFF3-MICRODATA.md`` on top of the
shared rules M1 to M4 and R9 in the family ``docs/MICRODATA.md`` and R7 and R9
in ``docs/FORMAT.md``. It is deliberately small and standard-library only
(``html.parser``, ``json``, ``re``). It is **not** a runtime parser: the reader
and writer shipped to users stay in the toolkit (FAIR-bioHeaders-Tools#58).
Tests use it to prove that the committed examples round-trip to their canonical
records, that the readable table matches the embedded metadata, and that the
negative fixtures are rejected.

The writer emits the converter's typed serialization (``data-fhr-type``
annotations, array containers with ``itemprop="item"`` children) so a typed
record can be recovered exactly. The reader also accepts the untyped fallback:
without ``data-fhr-type`` it converts values using the selected FHGFF3 JSON
Schema's types, as rule M3 requires.
"""

import json
from pathlib import Path
import re
from html import escape
from html.parser import HTMLParser

# The raw-main FHGFF3 schema URL is the record's itemtype identity
# (docs/SCHEMA-VERSIONS.md; docs/MICRODATA.md M1). The pre-rename repository
# name is the same file and the same item type.
FHGFF3_ITEMTYPE = (
    "https://raw.githubusercontent.com/FAIR-bioHeaders/"
    "FAIR-bioHeaders-Specification/main/fhgff3.json"
)
FHGFF3_ITEMTYPE_OLD_NAME = (
    "https://raw.githubusercontent.com/FAIR-bioHeaders/"
    "FHR-Specification/main/fhgff3.json"
)
FHGFF3_ITEMTYPES = {FHGFF3_ITEMTYPE, FHGFF3_ITEMTYPE_OLD_NAME}

# The `schema` itemprop selects the contract version. It is an FHGFF3 schema URL:
# a raw GitHub URL naming `main` or a release tag, or a w3id release URL
# (docs/SCHEMA-VERSIONS.md V1 to V4; docs/FHGFF3.md G3). Any other ref, or the
# FHR itemtype, is unsupported-version, not a fallback to another schema.
FHGFF3_SCHEMA_URL = re.compile(
    r"^https://raw\.githubusercontent\.com/FAIR-bioHeaders/"
    r"(FHR|FAIR-bioHeaders)-Specification/(main|v[0-9]+\.[0-9]+\.[0-9]+)/fhgff3\.json$"
)
FHGFF3_W3ID_URL = re.compile(
    r"^https://w3id\.org/fair-bioheaders/fhgff3/v[0-9]+\.[0-9]+\.[0-9]+/?$"
)

# The released FHGFF3 contract is schemaVersion "1.0" (schemas/versions.json).
FHGFF3_SCHEMA_VERSION = "1.0"

# Fixed releases this reader carries. They are copies of released schemas, not
# fetched at run time (docs/SCHEMA-VERSIONS.md V2 to V4). v0.4.1 carries the
# same FHGFF3 schema contract as v0.4.0.
RELEASES_DIR = Path(__file__).resolve().parent / "fixtures" / "releases"
SUPPORTED_RELEASES = {
    "v0.4.0": "fhgff3-v0.4.0.json",
    "v0.4.1": "fhgff3-v0.4.0.json",
}
_RELEASE_CACHE = {}

# Elements whose end tag HTML implies (docs/MICRODATA.md M2). The values are
# the ancestors a start tag closes, and the scope its search must not cross.
_VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
}
_BASE_SCOPE = {
    "applet", "caption", "html", "marquee", "object", "table", "td", "th",
    "template",
}
_BUTTON_SCOPE = _BASE_SCOPE | {"button"}
_LIST_SCOPE = _BASE_SCOPE | {"ol", "ul"}
_TABLE_SCOPE = {"html", "table", "template"}

# Start tags that close an open p in button scope.
_P_CLOSERS = {
    "address", "article", "aside", "blockquote", "details", "dialog", "div",
    "dl", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2",
    "h3", "h4", "h5", "h6", "header", "hgroup", "hr", "main", "menu", "nav",
    "ol", "p", "pre", "search", "section", "table", "ul",
    "li", "dt", "dd", "tr", "td", "th", "tbody", "thead", "tfoot",
}
_IMPLIED_BY_START = {
    "li": ({"li"}, _LIST_SCOPE),
    "dt": ({"dt", "dd"}, _BASE_SCOPE),
    "dd": ({"dt", "dd"}, _BASE_SCOPE),
    "option": ({"option"}, _BASE_SCOPE | {"select", "datalist"}),
    "optgroup": ({"option", "optgroup"}, _BASE_SCOPE | {"select"}),
    "tr": ({"tr"}, _TABLE_SCOPE),
    "td": ({"td", "th"}, _TABLE_SCOPE),
    "th": ({"td", "th"}, _TABLE_SCOPE),
    "tbody": ({"tbody", "thead", "tfoot"}, _TABLE_SCOPE),
    "thead": ({"tbody", "thead", "tfoot"}, _TABLE_SCOPE),
    "tfoot": ({"tbody", "thead", "tfoot"}, _TABLE_SCOPE),
    "colgroup": ({"colgroup"}, _TABLE_SCOPE),
}
# Elements whose defining attribute is the property value (docs/MICRODATA.md M2).
_VALUE_ATTRIBUTE = {
    "meta": "content",
    "a": "href", "area": "href", "link": "href",
    "audio": "src", "embed": "src", "iframe": "src", "img": "src",
    "source": "src", "track": "src", "video": "src",
    "object": "data",
    "data": "value", "meter": "value",
    "time": "datetime",
}
_TYPED = {"string", "integer", "number", "boolean", "null"}


class MicrodataError(ValueError):
    """The document is not valid FHGFF3 microdata."""


class _Node:
    __slots__ = ("tag", "attrs", "children", "itemscope", "itemtype", "itemprop",
                 "datatype")

    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = attrs
        self.children = []
        self.itemscope = "itemscope" in attrs
        self.itemtype = attrs.get("itemtype", "").split()
        self.itemprop = attrs.get("itemprop", "").split()
        self.datatype = attrs.get("data-fhr-type")


def _first_wins(attrs):
    """R9: the first of repeated attributes applies."""
    result = {}
    for name, value in attrs:
        if name not in result:
            result[name] = "" if value is None else value
    return result


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("#document", {})
        self.stack = [self.root]

    def _pop_through(self, targets, boundaries):
        """Close the nearest target ancestor and everything above it.

        The search skips inline descendants but stops at the scope boundary the
        HTML rule names, so an open span does not hide the p or table cell that
        the start tag has to close (docs/MICRODATA.md M2).
        """
        for index in range(len(self.stack) - 1, 0, -1):
            node = self.stack[index]
            if node.tag in targets:
                del self.stack[index:]
                return True
            if node.tag in boundaries:
                return False
        return False

    def _close_implied(self, tag):
        if tag in _P_CLOSERS:
            self._pop_through({"p"}, _BUTTON_SCOPE)
        rule = _IMPLIED_BY_START.get(tag)
        if rule:
            self._pop_through(*rule)

    def handle_starttag(self, tag, attrs):
        self._close_implied(tag)
        node = _Node(tag, _first_wins(attrs))
        self.stack[-1].children.append(node)
        if tag not in _VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(_Node(tag, _first_wins(attrs)))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _parse(text):
    builder = _TreeBuilder()
    builder.feed(text)
    builder.close()
    return builder.root


def _nodes(node):
    for child in node.children:
        if isinstance(child, _Node):
            yield child
            yield from _nodes(child)


def _text(node):
    parts = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif child.tag != "script":
            # Script contents are inert data, never metadata (H6).
            parts.append(_text(child))
    return "".join(parts)


def _value_of(element):
    attribute = _VALUE_ATTRIBUTE.get(element.tag)
    if attribute and attribute in element.attrs:
        return element.attrs[attribute]
    return _text(element)


def _resolve(root, subschema):
    while isinstance(subschema, dict) and "$ref" in subschema:
        reference = subschema["$ref"]
        if not reference.startswith("#/$defs/"):
            raise MicrodataError(f"unsupported $ref {reference!r}")
        subschema = root["$defs"][reference.rsplit("/", 1)[-1]]
    return subschema


def _json_type(root, subschema):
    resolved = _resolve(root, subschema)
    if "type" in resolved:
        return resolved["type"]
    branches = resolved.get("anyOf") or resolved.get("oneOf")
    if branches:
        types = {_json_type(root, branch) for branch in branches}
        if len(types) == 1:
            return types.pop()
    return None


def _subschema(root, parent, name):
    return _resolve(root, parent).get("properties", {}).get(name, {})


def _item_subschema(root, subschema):
    """The schema for one occurrence of a field, using an array's items."""
    resolved = _resolve(root, subschema)
    if _json_type(root, subschema) == "array":
        return resolved.get("items", {})
    return subschema


def _parse_typed(raw, datatype):
    if datatype == "string":
        return raw
    try:
        value = json.loads(raw)
    except ValueError as error:
        raise MicrodataError(f"{datatype} value is not JSON: {raw!r}") from error
    if datatype == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise MicrodataError(f"integer value is not an integer: {raw!r}")
    elif datatype == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise MicrodataError(f"number value is not a number: {raw!r}")
    elif datatype == "boolean":
        if not isinstance(value, bool):
            raise MicrodataError(f"boolean value is not a boolean: {raw!r}")
    elif datatype == "null":
        if value is not None:
            raise MicrodataError(f"null value is not null: {raw!r}")
    else:
        raise MicrodataError(f"unknown data-fhr-type {datatype!r}")
    return value


def _convert_untyped(raw, root, subschema):
    kind = _json_type(root, subschema)
    if kind in ("integer", "number", "boolean"):
        return _parse_typed(raw, kind)
    return raw


def _property_elements(scope):
    """Yield (element, property name) for the item's own properties (M1)."""
    def walk(node):
        for child in node.children:
            if not isinstance(child, _Node):
                continue
            if child.tag == "script":
                continue  # Script contents never contribute metadata (H6).
            if child.datatype in ("array", "object"):
                # A typed container's children are the container's own values,
                # not properties of the enclosing item.
                if child.itemprop:
                    for name in child.itemprop:
                        yield child, name
                continue
            if child.itemprop:
                for name in child.itemprop:
                    yield child, name
                if child.itemscope:
                    continue  # A nested item; its properties are not the parent's.
                # An ordinary property element can contain further properties;
                # they still belong to the enclosing item (M1).
                yield from walk(child)
            elif child.itemscope:
                continue  # A separate item; its properties are not the parent's.
            else:
                yield from walk(child)
    yield from walk(scope)


def _read_value(element, root, subschema):
    datatype = element.datatype
    if datatype == "array":
        items = []
        for child in element.children:
            if isinstance(child, str):
                if child.strip():
                    raise MicrodataError("array container has stray text")
                continue
            if "item" not in child.itemprop:
                raise MicrodataError("array container child is not itemprop=item")
            items.append(_read_value(child, root,
                                     _resolve(root, subschema).get("items", {})))
        return items
    # An array field may also appear as an ordinary occurrence (an untyped
    # item scope, or an explicitly typed object scope). Read it against the
    # item schema, not the array schema (M3).
    item_schema = _item_subschema(root, subschema)
    if datatype == "object":
        if not element.itemscope:
            raise MicrodataError("data-fhr-type=object without itemscope")
        return _read_scope(element, root, item_schema)
    if datatype in _TYPED:
        return _parse_typed(_value_of(element), datatype)
    if datatype is not None:
        raise MicrodataError(f"unknown data-fhr-type {datatype!r}")
    if element.itemscope:
        return _read_scope(element, root, item_schema)
    return _convert_untyped(_value_of(element), root, item_schema)


def _read_scope(scope, root, subschema):
    occurrences = {}
    for element, name in _property_elements(scope):
        value = _read_value(element, root, _subschema(root, subschema, name))
        occurrences.setdefault(name, []).append(value)
    record = {}
    for name, values in occurrences.items():
        field = _subschema(root, subschema, name)
        if _json_type(root, field) == "array":
            if len(values) == 1 and isinstance(values[0], list):
                # A single array container is unwrapped. Repeated containers
                # stay as nested lists, so schema validation rejects them
                # (docs/FHGFF3-MICRODATA.md H7).
                record[name] = values[0]
            else:
                # Ordinary repeated properties form one flat list (M4).
                record[name] = values
        elif len(values) == 1:
            record[name] = values[0]
        else:
            record[name] = values  # M4: a repeated property becomes a list.
    return record


def _release_schema(release):
    filename = SUPPORTED_RELEASES.get(release)
    if filename is None:
        supported = ", ".join(sorted(SUPPORTED_RELEASES))
        raise MicrodataError(
            f"unsupported FHGFF3 schema release: {release} "
            f"(this reader has FHGFF3 releases {supported})")
    if filename not in _RELEASE_CACHE:
        path = RELEASES_DIR / filename
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise MicrodataError(
                f"cannot load released FHGFF3 schema {release}: {error}") from error
        accepted = schema.get("properties", {}).get("schemaVersion", {}).get("enum")
        if accepted is not None and FHGFF3_SCHEMA_VERSION not in accepted:
            raise MicrodataError(
                f"released FHGFF3 schema {release} does not accept "
                f"schemaVersion {FHGFF3_SCHEMA_VERSION!r}")
        _RELEASE_CACHE[filename] = schema
    return _RELEASE_CACHE[filename]


def resolve_schema(selection, schema):
    """Resolve the FHGFF3 contract a record's ``schema`` value selects (H2).

    ``schema`` is the reader's current (``main``) schema. A released URL selects
    a fixed supported release; an unknown release or any other value is
    unsupported-version and is rejected before extraction or validation.
    """
    if not isinstance(selection, str):
        raise MicrodataError(f"unsupported FHGFF3 schema selection: {selection!r}")
    raw = FHGFF3_SCHEMA_URL.match(selection)
    if raw:
        ref = raw.group(2)
        return schema if ref == "main" else _release_schema(ref)
    w3id = FHGFF3_W3ID_URL.match(selection)
    if w3id:
        return _release_schema(w3id.group(0).rstrip("/").rsplit("/", 1)[-1])
    raise MicrodataError(f"unsupported FHGFF3 schema selection: {selection!r}")


def _selected_schema(scope, schema):
    for element, name in _property_elements(scope):
        if name == "schema":
            return resolve_schema(_value_of(element), schema)
    raise MicrodataError("FHGFF3 item scope has no schema property")


def read_page(text, schema=None):
    """Extract one FHGFF3 record from an HTML document.

    ``schema`` is the parsed current (``main``) FHGFF3 JSON Schema; it may be
    omitted when every value carries ``data-fhr-type``. The record's ``schema``
    value selects the contract first: ``main`` uses ``schema``, a supported
    release uses its released schema, and an unavailable release is rejected
    before validation (H2, V1 to V4). Raises :class:`MicrodataError` for a
    document that is not a single, structurally valid FHGFF3 item scope and for
    a ``schemaVersion`` the selected contract does not accept.
    """
    root_schema = schema if schema is not None else {}
    scope = _fhgff3_scope(text)
    selected_schema = _selected_schema(scope, root_schema)
    record = _read_scope(scope, selected_schema, selected_schema)
    accepted = _resolve(
        selected_schema,
        selected_schema.get("properties", {}).get("schemaVersion", {}),
    ).get("enum")
    version = record.get("schemaVersion")
    if accepted is not None and version not in accepted:
        raise MicrodataError(
            f"unsupported FHGFF3 schemaVersion: {version!r} "
            f"(the selected schema accepts {accepted!r})")
    return record


def _fhgff3_scope(text):
    scopes = [node for node in _nodes(_parse(text)) if node.itemscope]
    fhgff3_scopes = [node for node in scopes if FHGFF3_ITEMTYPES & set(node.itemtype)]
    if len(fhgff3_scopes) != 1:
        raise MicrodataError(
            f"expected exactly one FHGFF3 item scope, found {len(fhgff3_scopes)}")
    return fhgff3_scopes[0]


def _write_property(name, value):
    prop = escape(name, quote=True)
    if isinstance(value, dict):
        content = "".join(_write_property(key, item) for key, item in value.items())
        return f'<span itemprop="{prop}" itemscope data-fhr-type="object">{content}</span>'
    if isinstance(value, list):
        content = "".join(_write_property("item", item) for item in value)
        return f'<span itemprop="{prop}" data-fhr-type="array">{content}</span>'
    if isinstance(value, bool):
        datatype, text = "boolean", json.dumps(value)
    elif isinstance(value, int):
        datatype, text = "integer", json.dumps(value)
    elif isinstance(value, float):
        datatype, text = "number", json.dumps(value)
    else:
        datatype, text = "string", value
    return f'<span itemprop="{prop}" data-fhr-type="{datatype}">{escape(text)}</span>'


def to_json(record):
    """The canonical JSON serialization of a record."""
    return json.dumps(record, ensure_ascii=False, indent=2) + "\n"


def _yaml_scalar(value):
    """A deterministic, JSON-compatible YAML scalar (valid under YAML 1.2)."""
    if isinstance(value, bool) or isinstance(value, (int, float)):
        return json.dumps(value)
    if value is None:
        return "null"
    return json.dumps(str(value), ensure_ascii=False)


def _yaml_lines(value, indent):
    pad = " " * indent
    lines = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, dict):
                if item:
                    lines.append(f"{pad}{key}:")
                    lines.extend(_yaml_lines(item, indent + 2))
                else:
                    lines.append(f"{pad}{key}: {{}}")
            elif isinstance(item, list):
                if item:
                    lines.append(f"{pad}{key}:")
                    lines.extend(_yaml_lines(item, indent + 2))
                else:
                    lines.append(f"{pad}{key}: []")
            else:
                lines.append(f"{pad}{key}: {_yaml_scalar(item)}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                if item:
                    item_lines = _yaml_lines(item, indent + 2)
                    lines.append(f"{pad}- {item_lines[0].lstrip()}")
                    lines.extend(item_lines[1:])
                else:
                    lines.append(f"{pad}- {{}}")
            elif isinstance(item, list):
                if item:
                    lines.append(f"{pad}-")
                    lines.extend(_yaml_lines(item, indent + 2))
                else:
                    lines.append(f"{pad}- []")
            else:
                lines.append(f"{pad}- {_yaml_scalar(item)}")
    return lines


def to_yaml(record):
    """The canonical YAML serialization, equivalent to :func:`to_json`.

    Strings are double-quoted (JSON-compatible escapes), so values YAML would
    otherwise retype, such as the quoted ``schemaVersion`` and dates, stay
    strings. This is a test-only writer, not the toolkit's.
    """
    return "\n".join(_yaml_lines(record, 0)) + "\n"


def table_rows(record):
    """The readable-table rows for a record, as (label, value) strings.

    The table is a human summary only. It repeats values that are also in the
    embedded microdata so the two can be compared; it adds no metadata and is
    never read back as metadata.
    """
    rows = [
        ("Annotation", str(record["annotation"])),
        ("Version", str(record["version"])),
    ]
    taxon = record.get("taxon")
    if taxon:
        rows.append(("Taxon", f'{taxon.get("name", "")} ({taxon.get("uri", "")})'))
    reference = record.get("genomeReference")
    if reference:
        parts = [str(reference.get("accession", ""))]
        if "seqcol_id" in reference:
            parts.append("seqcol=" + str(reference["seqcol_id"]))
        if "assemblyName" in reference:
            parts.append("assembly=" + str(reference["assemblyName"]))
        rows.append(("Genome reference (asserted)", " ".join(p for p in parts if p)))
    parents = record.get("derivedFrom", [])
    annotates = [p for p in parents if p.get("relationship") == "annotates"]
    if annotates:
        parent = annotates[0]
        rows.append(("Annotated genome parent (FHR checksum)",
                     f'{parent.get("headerType", "")} {parent.get("checksum", "")}'.strip()))
    others = [p for p in parents if p.get("relationship") != "annotates"]
    if others:
        rows.append(("Other parents",
                     "; ".join(f'{p.get("headerType", "")}:{p.get("relationship", "")}'
                               for p in others)))
    authors = record.get("metadataAuthor", [])
    if authors:
        rows.append(("Metadata authors", "; ".join(a.get("name", "") for a in authors)))
    software = record.get("annotationSoftware", [])
    if software:
        rows.append(("Annotation software",
                     "; ".join(f'{s.get("name", "")} {s.get("version", "")}'.strip()
                               for s in software)))
    counts = record.get("featureCounts", [])
    if counts:
        rows.append(("Feature counts (producer assertion)",
                     "; ".join(f'{c["featureType"]}={c["count"]}' for c in counts)))
    completeness = record.get("completeness")
    if completeness:
        rows.append(("Completeness (BUSCO counts)",
                     "S:{completeSingle} D:{completeDuplicated} F:{fragmented} "
                     "M:{missing} n:{total}".format(**completeness)))
    if "documentation" in record:
        rows.append(("Documentation", str(record["documentation"])))
    rows.append(("Checksum (ordinary value; not verified here)", str(record["checksum"])))
    return rows


def write_page(record, itemtype=FHGFF3_ITEMTYPE, title="FHGFF3 microdata example"):
    """Write one record as a standalone HTML document with a readable table."""
    content = "".join(_write_property(name, value) for name, value in record.items())
    rows = "".join(
        f"<tr><td>{escape(label)}</td><td>{escape(value)}</td></tr>"
        for label, value in table_rows(record)
    )
    table = (
        "<table><caption>FHGFF3 metadata (human summary)</caption>"
        "<tr><th>Property</th><th>Value</th></tr>" + rows + "</table>"
    )
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        f"<title>{escape(title)}</title></head><body>\n"
        f'<div itemscope itemtype="{escape(itemtype, quote=True)}">{content}</div>\n'
        f"{table}\n"
        "</body></html>\n"
    )


def read_table(text):
    """Extract the readable table's (label, value) rows from a document.

    Only the first table's two-cell data rows are returned; the header row and
    any caption are ignored. This is a test helper, not a metadata reader.
    """
    for node in _nodes(_parse(text)):
        if node.tag != "table":
            continue
        rows = []
        for row in _nodes(node):
            if row.tag != "tr":
                continue
            cells = [child for child in row.children
                     if isinstance(child, _Node) and child.tag in ("td", "th")]
            if len(cells) == 2 and cells[0].tag == "td" and cells[1].tag == "td":
                rows.append((_text(cells[0]), _text(cells[1])))
        return rows
    return []
