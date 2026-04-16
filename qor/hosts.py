"""Host-to-install-path resolver for qorlogic CLI.

Maps AI coding host names to filesystem targets for skill/agent installation.
Extensible: instantiate HostTarget directly for custom paths.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


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
    """Kilo Code default paths."""
    base = Path.home() / ".kilo-code"
    return HostTarget(
        name="kilo-code",
        skills_dir=base / "skills",
        agents_dir=base / "agents",
    )


_HOSTS = {
    "claude": _claude_target,
    "kilo-code": _kilo_target,
}


def resolve(host_name: str, target_override: Path | None = None) -> HostTarget:
    """Resolve a host name to a HostTarget.

    If target_override is set, skills_dir and agents_dir point into it.
    Raises ValueError for unknown hosts, NotImplementedError for codex.
    """
    if host_name == "codex":
        raise NotImplementedError("codex install paths TBD")

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
