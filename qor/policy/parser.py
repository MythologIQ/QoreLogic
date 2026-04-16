"""Cedar subset parser.

Parses a restricted Cedar syntax supporting:
- ``permit`` / ``forbid`` effects
- ``==`` and ``in`` constraints on principal/action/resource
- ``when { lhs == rhs; ... }`` condition blocks
- Unconstrained slots (bare ``principal``, ``action``, ``resource``)

No support for ``unless``, ``has``, IP/decimal extensions.
"""
from __future__ import annotations

import re
from pathlib import Path

from qor.policy.types import Condition, Constraint, EntityUID, Policy


def _strip_comments(text: str) -> str:
    """Remove // line comments."""
    return re.sub(r"//[^\n]*", "", text)


def _parse_entity_uid(raw: str) -> EntityUID:
    """Parse ``Type::"id"`` into EntityUID."""
    m = re.match(r'(\w+)::"([^"]+)"', raw.strip())
    if not m:
        raise ValueError(f"invalid EntityUID: {raw!r}")
    return EntityUID(type=m.group(1), id=m.group(2))


def _parse_constraint(slot_name: str, raw: str) -> Constraint:
    """Parse a single constraint clause like ``principal == Skill::"x"``."""
    raw = raw.strip().rstrip(",")
    # Unconstrained: just the slot name
    if raw == slot_name:
        return Constraint()
    # == constraint
    m = re.match(rf"{slot_name}\s*==\s*(.+)", raw)
    if m:
        return Constraint(op="==", entity=_parse_entity_uid(m.group(1)))
    # in constraint
    m = re.match(rf"{slot_name}\s+in\s+(.+)", raw)
    if m:
        return Constraint(op="in", entity=_parse_entity_uid(m.group(1)))
    raise ValueError(f"cannot parse {slot_name} constraint: {raw!r}")


def _parse_conditions(when_block: str) -> list[Condition]:
    """Parse conditions from a ``when { ... }`` block body."""
    conditions: list[Condition] = []
    # Split on semicolons, handle each statement
    stmts = [s.strip() for s in when_block.split(";") if s.strip()]
    for stmt in stmts:
        # lhs == rhs
        m = re.match(r"(.+?)\s*==\s*(.+)", stmt)
        if m:
            conditions.append(Condition(
                lhs=m.group(1).strip(),
                op="==",
                rhs=m.group(2).strip().strip('"'),
            ))
            continue
        # lhs in rhs
        m = re.match(r"(.+?)\s+in\s+(.+)", stmt)
        if m:
            conditions.append(Condition(
                lhs=m.group(1).strip(),
                op="in",
                rhs=m.group(2).strip().strip('"'),
            ))
            continue
        raise ValueError(f"cannot parse condition: {stmt!r}")
    return conditions


def _split_policy_blocks(text: str) -> list[str]:
    """Split text into individual policy blocks."""
    blocks: list[str] = []
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "(" and start < 0:
            # Look backwards for permit/forbid keyword
            prefix = text[:i].rstrip()
            if prefix.endswith("permit") or prefix.endswith("forbid"):
                start = prefix.rfind("permit") if prefix.endswith("permit") else prefix.rfind("forbid")
                depth = 0
        if start >= 0:
            if ch in "({":
                depth += 1
            elif ch in ")}":
                depth -= 1
                if depth == 0 and ch == ";":
                    blocks.append(text[start:i + 1])
                    start = -1
            # End of policy: after closing "}" or ")" with semicolon
            if depth == 0 and i > start and ch == ";":
                blocks.append(text[start:i + 1])
                start = -1
    # Handle block without trailing semicolon
    if start >= 0:
        blocks.append(text[start:].rstrip())
    return blocks


def parse_policy(text: str, policy_id: str = "policy_0") -> Policy:
    """Parse a single policy block."""
    text = text.strip()
    # Extract effect
    m = re.match(r"(permit|forbid)\s*\(", text)
    if not m:
        raise ValueError(f"expected permit/forbid, got: {text[:30]!r}")
    effect = m.group(1)

    # Extract the scope (inside parens)
    paren_start = text.index("(")
    depth = 0
    paren_end = paren_start
    for i in range(paren_start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                paren_end = i
                break
    scope_body = text[paren_start + 1:paren_end]

    # Split scope into principal, action, resource
    parts = [p.strip() for p in scope_body.split(",") if p.strip()]
    principal = Constraint()
    action = Constraint()
    resource = Constraint()
    for part in parts:
        if part.startswith("principal"):
            principal = _parse_constraint("principal", part)
        elif part.startswith("action"):
            action = _parse_constraint("action", part)
        elif part.startswith("resource"):
            resource = _parse_constraint("resource", part)

    # Extract when block if present
    conditions: list[Condition] = []
    when_match = re.search(r"when\s*\{([^}]*)\}", text[paren_end:])
    if when_match:
        conditions = _parse_conditions(when_match.group(1))

    return Policy(
        id=policy_id,
        effect=effect,
        principal=principal,
        action=action,
        resource=resource,
        conditions=conditions,
    )


def parse_policies(text: str, base_id: str = "policy") -> list[Policy]:
    """Parse multiple policies from Cedar text."""
    text = _strip_comments(text)
    # Use regex to find each permit/forbid block
    pattern = re.compile(
        r"((?:permit|forbid)\s*\([^)]*\)\s*(?:when\s*\{[^}]*\}\s*)?);?",
        re.DOTALL,
    )
    policies: list[Policy] = []
    for i, m in enumerate(pattern.finditer(text)):
        pid = f"{base_id}_{i}"
        policies.append(parse_policy(m.group(1), policy_id=pid))
    return policies


def parse_file(path: Path) -> list[Policy]:
    """Parse a .cedar file into a list of policies."""
    text = path.read_text(encoding="utf-8")
    base_id = path.stem
    return parse_policies(text, base_id=base_id)
