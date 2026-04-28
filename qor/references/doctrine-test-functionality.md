# Doctrine: Test Functionality (not Presence)

**Source**: Phase 45 v1 lesson — attribution-trailer doc-consistency tests asserted only `<string> in <file_text>`. Cross-references SG-035 (doctrine-content test unanchored) in `qor/references/doctrine-shadow-genome-countermeasures.md`.

**Goal**: A test means something only when it would catch the unit under test silently breaking. Presence-only assertions pass vacuously when the artifact survives but the behavior decays.

## Principle

A test must verify the unit under test does the right thing. Asserting only that a file exists, a string appears in a file, a function is defined, or a configuration key is set is insufficient on its own — the test passes vacuously if the artifact survives but the behavior breaks.

## Definitions

- **Presence-only test**: an assertion that is solely about the existence or textual presence of an artifact (file path, substring, attribute, declaration). The unit under test is not invoked; no output is compared to an expected value.
- **Functionality test**: a test that invokes the unit (function call, CLI subprocess, helper rendering, parser pass) and asserts the call's return value or observable side-effect against an expected value computed from the inputs.

## Rule

Every test of a unit's behavior MUST invoke that unit and assert against its output. Drift-guards (output-vs-documentation surface checks) are acceptable as auxiliary tests, but the primary test of the unit's behavior MUST be a functionality test, not a presence check.

Acceptance question, applied to every new test: *"If the unit's behavior were silently broken but the artifact still existed, would this test fail?"* If no, the test is presence-only and must be rewritten.

## Anti-patterns (verified instances)

| Anti-pattern | Where seen | Lesson |
|---|---|---|
| Substring-only doc-consistency check | Phase 45 attribution-trailer tests | A `Co-Authored-By:` substring presence check passes even if `git interpret-trailers --parse` would reject the rendered output. The behavioral test must run `git interpret-trailers --parse` (or the equivalent parser the runtime relies on) and assert the parsed output. |
| Doctrine-content test unanchored | SG-035 (Phase 15 v1, Entry #36 V-2) | Same family: substring presence with no anchor passes when the doctrine section is absent but the keyword co-occurs elsewhere. Anchor every keyword check to a section header and pair it with a strip-and-fail negative-path test. |
| Skill-prompt enforcement landed without anchor | Phase 46 (this doctrine) | A naive lock like `assert "presence-only" in body` would pass even after the section was deleted, as long as the keyword occurred anywhere else in the file. Mitigation: every Phase 46 doctrine assertion is paired with a strip-and-fail test that proves the assertion fails when the named section is removed. |

## Verification mechanisms

- `tests/test_doctrine_test_functionality.py` locks each gate skill's enforcement language to its section header. Every positive proximity-anchor assertion is paired with a strip-and-fail negative-path test, so the doctrine test cannot itself decay into a presence-only check.
- `/qor-plan` Step 4 forbids presence-only test descriptions in plan files; Step 5 reviews behavior-naming on every described test.
- `/qor-audit` Test Functionality Pass vetoes any plan whose described tests do not invoke the unit under test.
- `/qor-implement` Step 5 (TDD-Light) requires the failing test invoke the unit; Step 9 scans newly-added tests for the `assert <substring> in <file_text>` family.
- `/qor-substantiate` Step 4 Test Audit refuses to seal if a phase-added test is presence-only for the unit it claims to cover.

## Update protocol

When a new presence-only failure mode emerges, append to the Anti-patterns table with a where-seen citation. The doctrine grows with the project's failure history; it does not shrink.
