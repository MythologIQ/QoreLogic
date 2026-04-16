"""Cedar-inspired policy evaluator.

Evaluates a Request against a set of Policies:
- Default DENY (no matching permit -> deny)
- Any matching ``forbid`` overrides all ``permit`` matches
- Returns Decision + list of matching policy IDs for audit trail
"""
from __future__ import annotations

from dataclasses import dataclass, field

from qor.policy.types import (
    Condition,
    Constraint,
    Decision,
    EntityUID,
    Policy,
    Request,
)


@dataclass
class EvalResult:
    """Evaluation result with audit trail."""
    decision: Decision
    matching_policies: list[str] = field(default_factory=list)


def _match_constraint(
    constraint: Constraint,
    entity: EntityUID,
    groups: dict[str, list[str]] | None = None,
) -> bool:
    """Check if an entity satisfies a constraint."""
    if constraint.op is None:
        return True  # unconstrained
    if constraint.entity is None:
        return True
    if constraint.op == "==":
        return (entity.type == constraint.entity.type
                and entity.id == constraint.entity.id)
    if constraint.op == "in":
        if groups is None:
            return False
        group_key = str(constraint.entity)
        members = groups.get(group_key, [])
        return str(entity) in members
    return False


def _resolve_attr(name: str, request: Request, entities: dict) -> str | bool | None:
    """Resolve a dotted attribute reference against request context or entities."""
    # resource.verdict -> look up in entities or context
    parts = name.split(".", 1)
    if len(parts) == 2:
        slot, attr = parts
        if slot == "resource":
            # Check entities first
            entity_key = str(request.resource)
            if entity_key in entities:
                entity_attrs = entities[entity_key]
                if attr in entity_attrs:
                    return entity_attrs[attr]
            # Fall back to context
            return request.context.get(attr)
        if slot == "principal":
            entity_key = str(request.principal)
            if entity_key in entities:
                return entities[entity_key].get(attr)
        if slot == "context":
            return request.context.get(attr)
    # Direct context lookup
    return request.context.get(name)


def _eval_condition(
    cond: Condition,
    request: Request,
    entities: dict,
) -> bool:
    """Evaluate a single condition against request + entities."""
    lhs_val = _resolve_attr(cond.lhs, request, entities)
    rhs_val: str | bool = cond.rhs
    # Coerce boolean strings
    if rhs_val == "true":
        rhs_val = True
    elif rhs_val == "false":
        rhs_val = False
    if cond.op == "==":
        return lhs_val == rhs_val
    if cond.op == "in":
        if isinstance(lhs_val, (list, tuple, set)):
            return rhs_val in lhs_val
        return False
    return False


def _policy_matches(
    policy: Policy,
    request: Request,
    entities: dict,
    groups: dict[str, list[str]] | None = None,
) -> bool:
    """Check if a policy's scope and conditions match the request."""
    if not _match_constraint(policy.principal, request.principal, groups):
        return False
    if not _match_constraint(policy.action, request.action, groups):
        return False
    if not _match_constraint(policy.resource, request.resource, groups):
        return False
    # All conditions must hold
    for cond in policy.conditions:
        if not _eval_condition(cond, request, entities):
            return False
    return True


def evaluate(
    request: Request,
    policies: list[Policy],
    entities: dict | None = None,
    groups: dict[str, list[str]] | None = None,
) -> EvalResult:
    """Evaluate a request against a policy set.

    Returns EvalResult with decision and matching policy IDs.
    Default DENY: no matching permit means deny.
    Any matching forbid overrides all permits.
    """
    if entities is None:
        entities = {}

    permits: list[str] = []
    forbids: list[str] = []

    for policy in policies:
        if _policy_matches(policy, request, entities, groups):
            if policy.effect == "permit":
                permits.append(policy.id)
            elif policy.effect == "forbid":
                forbids.append(policy.id)

    if forbids:
        return EvalResult(
            decision=Decision.DENY,
            matching_policies=forbids + permits,
        )
    if permits:
        return EvalResult(
            decision=Decision.ALLOW,
            matching_policies=permits,
        )
    return EvalResult(decision=Decision.DENY, matching_policies=[])
