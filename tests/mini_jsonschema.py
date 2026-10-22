# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""A tiny JSON Schema subset validator for the FHGFF3 tests.

The released ``fhgff3.json`` is a Draft 2020-12 schema, but the test environment
has no ``jsonschema`` distribution (the ``jsonschema/`` directory in this tree
is the inherited generated feature model, not the library). This module is a
**test-only**, standard-library stand-in that supports exactly the keywords the
FHGFF3 schema uses: ``$ref``/``$defs``, ``type``, ``properties``, ``required``,
``additionalProperties: false``, ``items``, ``contains``/``minContains``,
``enum``, ``const``, ``pattern``, ``minLength``/``maxLength``, ``minimum``,
``anyOf``, ``allOf``, ``not`` and ``if``/``then``, plus the ``date`` and ``uri``
formats.

It is not a general validator and is not shipped. The fixtures in
``examples/fhgff3/`` and the binding in ``docs/FHGFF3-MICRODATA.md`` are the
reviewed artifacts; this module only lets the tests say that the extracted
metadata validates against the released ``fhgff3.json``.
"""

from datetime import date
import re
from urllib.parse import urlsplit

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}
_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*$")
# Schemes that use an authority (host) and so need one to be a usable URI.
_HIERARCHICAL_SCHEMES = {"http", "https", "ftp", "ftps", "ws", "wss"}
_FORBIDDEN_HOST_CHARS = set('<>"{}|\\^`')


def _is_date(value):
    """RFC 3339 full-date: exact ``YYYY-MM-DD`` shape and a real calendar date.

    Test-only: ``date.fromisoformat`` rejects impossible dates such as
    ``2026-99-99`` or ``2026-02-30`` that a shape-only regex would accept.
    """
    if not _DATE.match(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _is_uri(value):
    """A syntactically usable URI, not just a scheme prefix.

    Test-only stand-in for the JSON Schema ``uri`` format. ``urlsplit`` parses
    the value so malformed IPv6 brackets and bad ports raise, and HTTP(S)-style
    schemes must have a non-empty, whitespace-free host.
    """
    if any(char.isspace() or ord(char) < 0x20 or ord(char) == 0x7F
           for char in value):
        return False
    try:
        parts = urlsplit(value)
        parts.port  # raises ValueError for a non-numeric or out-of-range port
    except ValueError:
        return False
    if not _SCHEME.match(parts.scheme):
        return False
    if parts.scheme.lower() in _HIERARCHICAL_SCHEMES:
        if not parts.netloc or not parts.hostname:
            return False
        if any(char in _FORBIDDEN_HOST_CHARS for char in parts.netloc):
            return False
    return True


class ValidationError(ValueError):
    """One JSON Schema validation failure."""

    def __init__(self, path, message):
        super().__init__(f"{path or '/'}: {message}")
        self.path = path
        self.message = message


def _json_equal(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _json_equal(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(map(_json_equal, left, right))
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    return type(left) is type(right) and left == right


def _is_type(instance, name):
    if name == "boolean":
        return isinstance(instance, bool)
    if name in ("integer", "number") and isinstance(instance, bool):
        return False
    return isinstance(instance, _TYPES[name])


def _resolve(root, subschema):
    while isinstance(subschema, dict) and "$ref" in subschema:
        reference = subschema["$ref"]
        if not reference.startswith("#/$defs/"):
            raise ValidationError("", f"unsupported $ref {reference!r}")
        subschema = root["$defs"][reference.rsplit("/", 1)[-1]]
    return subschema


def _iter(instance, subschema, root, path):
    subschema = _resolve(root, subschema)
    if not isinstance(subschema, dict):
        return

    for branch in subschema.get("allOf", []):
        yield from _iter(instance, branch, root, path)

    if "anyOf" in subschema:
        if not any(not list(_iter(instance, branch, root, path))
                   for branch in subschema["anyOf"]):
            yield ValidationError(path, "does not match any anyOf branch")

    if "not" in subschema:
        if not list(_iter(instance, subschema["not"], root, path)):
            yield ValidationError(path, "matches a forbidden 'not' subschema")

    if "if" in subschema:
        if not list(_iter(instance, subschema["if"], root, path)):
            if "then" in subschema:
                yield from _iter(instance, subschema["then"], root, path)
            if "else" in subschema:
                yield from _iter(instance, subschema["else"], root, path)

    if "const" in subschema and not _json_equal(instance, subschema["const"]):
        yield ValidationError(path, f"is not the constant {subschema['const']!r}")

    if "enum" in subschema and not any(
            _json_equal(instance, choice) for choice in subschema["enum"]):
        yield ValidationError(path, f"is not one of {subschema['enum']!r}")

    if "type" in subschema:
        names = subschema["type"]
        names = names if isinstance(names, list) else [names]
        if not any(_is_type(instance, name) for name in names):
            yield ValidationError(path, f"is not of type {subschema['type']!r}")
            return

    if isinstance(instance, bool):
        return

    if isinstance(instance, (int, float)):
        if "minimum" in subschema and instance < subschema["minimum"]:
            yield ValidationError(
                path, f"is less than the minimum {subschema['minimum']}")

    if isinstance(instance, str):
        if "minLength" in subschema and len(instance) < subschema["minLength"]:
            yield ValidationError(
                path, f"is shorter than minLength {subschema['minLength']}")
        if "maxLength" in subschema and len(instance) > subschema["maxLength"]:
            yield ValidationError(
                path, f"is longer than maxLength {subschema['maxLength']}")
        if "pattern" in subschema and not re.search(subschema["pattern"], instance):
            yield ValidationError(
                path, f"does not match pattern {subschema['pattern']!r}")
        if subschema.get("format") == "date" and not _is_date(instance):
            yield ValidationError(path, "is not a date")
        if subschema.get("format") == "uri" and not _is_uri(instance):
            yield ValidationError(path, "is not a URI")

    if isinstance(instance, dict):
        for name in subschema.get("required", []):
            if name not in instance:
                yield ValidationError(path, f"is missing the required property {name!r}")
        properties = subschema.get("properties", {})
        if subschema.get("additionalProperties") is False:
            for name in instance:
                if name not in properties:
                    yield ValidationError(
                        path, f"has the additional property {name!r}")
        for name, value in instance.items():
            if name in properties:
                yield from _iter(value, properties[name], root, f"{path}/{name}")

    if isinstance(instance, list):
        items = subschema.get("items")
        if isinstance(items, dict):
            for index, value in enumerate(instance):
                yield from _iter(value, items, root, f"{path}/{index}")
        if "contains" in subschema:
            matches = sum(
                1 for value in instance
                if not list(_iter(value, subschema["contains"], root, path)))
            minimum = subschema.get("minContains", 1)
            if matches < minimum:
                yield ValidationError(
                    path, f"has fewer than minContains ({minimum}) matching items")
            if "maxContains" in subschema and matches > subschema["maxContains"]:
                yield ValidationError(
                    path, f"has more than maxContains ({subschema['maxContains']}) "
                          "matching items")


def iter_errors(instance, schema):
    """Yield :class:`ValidationError` for ``instance`` against ``schema``."""
    return _iter(instance, schema, schema, "")


def validate(instance, schema):
    """Raise the first :class:`ValidationError`, or return ``instance``."""
    for error in iter_errors(instance, schema):
        raise error
    return instance
