# Declared-reference advisory audit

This consumer implements its part of
[shared issue #241](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/issues/241).
The adapter reads this repository's **current owning declarations** on every run;
it does not score the central inventory's older snapshot or change any pin.

`checker.json` pins the accepted shared checker by source commit and SHA-256.
The runner verifies the approved repository, full commit, canonical nonsymlink path, checkout HEAD, immutable `git show <commit>:<path>` bytes and script digest before execution. The working file must equal that committed blob even if both it and the recorded digest were tampered with. The verified engine runs under Python `-I`, isolating unverified adjacent modules. The
engine is not copied here. Schema, model, suite, carrier and historical copy
pins remain unchanged. A checker-code refresh is a separate reviewed change.

## Scope

Current `header/provenance.json` declares 49 byte-copied header paths and 4 unvendored
imports. Explicit source patterns cover the complete selected header scope;
local set comparison excludes only the named authored landing/provenance files.
The suite manifest has its own recorded commit/digest; models/rules and the
released header tree resolve at the declared release tag. Unvendored imports
have no fictitious local-copy assertion.

The inherited biodatamodels/gff-schema model remains under the accepted no-reuse
boundary and is outside FAIR contract retrieval. No inherited model build or
redistribution is enabled. Existing header parity remains required; this audit
adds independent authority and full path-set reporting.

## Local commands and evidence

```sh
python3 -m unittest discover -s tests -p test_reference_audit.py -v
python3 scripts/reference_audit.py --inventory-only
python3 scripts/reference_audit.py --checker-root /path/to/pinned/shared --checkout FAIR-bioHeaders/FAIR-bioHeaders-Specification=/path/to/pinned/shared
python3 scripts/check_reference_audit_controls.py --checker-root /path/to/pinned/shared
```

The shared checkout must be at the exact checker commit and have all referenced
release tags/history available. Required controls use a temporary synthetic Git
repository, exercising FRESH, deliberately changed-byte DRIFT, confirmed ABSENT,
and unmapped QUERY_FAILED outcomes with the actual checker. They never depend on
current owning references remaining fresh. PR checks retain the current-reference
report without gating on its findings; existing native contract/parity gates
remain independent. An always-run fallback retains QUERY_FAILED if setup or
execution produced no usable report. Execution failures may still fail the job;
reference findings do not. No fixture, pin or source file is rewritten.

The scheduled/manual job checks authoritative tag/commit bytes over the GitHub
API with read-only permissions and retains the generated inventory and JSON
report. Its normal exit is advisory: inspect every FRESH/DRIFT/ABSENT/QUERY_FAILED
result and the explicit local/source-set coverage. An unusable declaration or
unverified checker refuses execution with exit 2. Failed queries are not missing
artifacts, and an unperformed comparison is not a pass. No auto-repin runs.

The checks establish fidelity to the declared revision, not adoption, latest-main
currency, biological validity or a new contract release. Other consumers still
need their own actual rollout before the federation-wide issue can close.

Controlling source repository/URL declarations are validated before normalization; missing or unexpected authorities refuse the run instead of being silently replaced with the publication authority. Historical observations and namespace `$id` values are not retrieval inputs.

The bootstrap disables Git replacement objects, verifies exact committed bytes,
and executes a private snapshot of those verified bytes until the subprocess
finishes. A later change to the source checkout cannot change that executable.
Identifiable missing revision/commit/path/digest declarations remain incomplete data for
the central engine's ABSENT classification; supplied floating references remain
DRIFT inputs. Conflicting source authorities or malformed supplied metadata
refuse normalization, with an observable QUERY_FAILED execution fallback.

The checker-code update selects the independently reviewed shared PR280
implementation. Consumer merge remains dependent on that central PR merging;
contract, suite, copied-source and carrier selections are unchanged.

The required synthetic controls also prove missing recorded tag commit, revision,
path and digest become ABSENT; supplied floating main becomes DRIFT; and a missing
copied file remains ABSENT through complete source/local set comparisons.
