"""Cedar-inspired policy data types.

Pure Python types modelling a subset of the Cedar policy language:
EntityUID, Request, Decision, and Policy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class EntityUID:
    """Entity identifier: ``Type::"id"``."""
    type: str
    id: str

    def __str__(self) -> str:
        return f'{self.type}::"{self.id}"'


class Decision(Enum):
    """Policy evaluation outcome."""
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True)
class Condition:
    """A single ``when`` clause condition: ``lhs == rhs`` or ``lhs in rhs``."""
    lhs: str
    op: str   # "==" or "in"
    rhs: str


@dataclass(frozen=True)
class Constraint:
    """Principal/action/resource constraint.

    If ``entity`` is None the constraint is unconstrained (matches any).
    ``op`` is "==" or "in".
    """
    op: str | None = None
    entity: EntityUID | None = None


@dataclass(frozen=True)
class Policy:
    """A single Cedar-style policy."""
    id: str
    effect: str   # "permit" or "forbid"
    principal: Constraint = field(default_factory=lambda: Constraint())
    action: Constraint = field(default_factory=lambda: Constraint())
    resource: Constraint = field(default_factory=lambda: Constraint())
    conditions: list[Condition] = field(default_factory=list)


@dataclass(frozen=True)
class Request:
    """Authorization request."""
    principal: EntityUID
    action: EntityUID
    resource: EntityUID
    context: dict = field(default_factory=dict)
