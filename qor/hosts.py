"""Host-to-install-path resolver for qorlogic CLI.

Maps AI coding host names to filesystem targets for skill/agent installation.
Extensible via ``register_host()`` for third-party hosts (Cursor, Continue,
Windsurf, Aider).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class HostTarget:
    """Install target for a specific AI coding host."""
    name: str
    skills_dir: Path
    agents_dir: Path


def _claude_target() -> HostTarget:
    """Claude Code default paths. Respects $CLAUDE_PROJECT_DIR."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        base = Path(project_dir) / ".claude"
    else:
        base = Path.home() / ".claude"
    return HostTarget(
        name="claude",
        skills_dir=base / "skills",
        agents_dir=base / "agents",
    )


def _kilo_target() -> HostTarget:
    """Kilo Code default paths (provisional: ~/.kilo-code/).

    Kilo Code's actual skill directory convention is configurable
    via --target; default ~/.kilo-code/ is provisional.
    """
    base = Path.home() / ".kilo-code"
    return HostTarget(
        name="kilo-code",
        skills_dir=base / "skills",
        agents_dir=base / "agents",
    )


def _codex_target() -> HostTarget:
    """Codex provisional paths (~/.codex/skills/).

    Format TBD; identity-copy of claude variant for now.
    """
    base = Path.home() / ".codex"
    return HostTarget(
        name="codex",
        skills_dir=base / "skills",
        agents_dir=base / "agents",
    )


_HOSTS: dict[str, Callable[[], HostTarget]] = {
    "claude": _claude_target,
    "kilo-code": _kilo_target,
    "codex": _codex_target,
}


def register_host(name: str, factory: Callable[[], HostTarget]) -> None:
    """Register a third-party host factory (Cursor, Continue, Windsurf, etc.).

    Overwrites any existing factory for the same name.
    """
    _HOSTS[name] = factory


def resolve(host_name: str, target_override: Path | None = None) -> HostTarget:
    """Resolve a host name to a HostTarget.

    If target_override is set, skills_dir and agents_dir point into it.
    Raises ValueError for unknown hosts.
    """
    factory = _HOSTS.get(host_name)
    if factory is None:
        raise ValueError(f"unknown host: {host_name!r}")

    if target_override is not None:
        return HostTarget(
            name=host_name,
            skills_dir=target_override / "skills",
            agents_dir=target_override / "agents",
        )
    return factory()
