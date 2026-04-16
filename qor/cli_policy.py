"""CLI handlers for policy and init subcommands."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def do_init(args: argparse.Namespace) -> int:
    """Initialize a .qorlogic/config.json in the current directory."""
    config_dir = Path.cwd() / ".qorlogic"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"

    host = getattr(args, "host", "claude")
    profile = getattr(args, "profile", "sdlc")
    target = getattr(args, "target", None)

    config = {
        "host": host,
        "profile": profile,
        "target": str(target) if target else None,
        "governance_scope": "git_root" if profile == "sdlc" else "cwd",
    }
    config_path.write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8",
    )
    print(f"Initialized .qorlogic/config.json (host={host}, profile={profile})")
    return 0


def do_policy_check(args: argparse.Namespace) -> int:
    """Evaluate a JSON request against .cedar policies."""
    from qor.policy import Decision, EntityUID, Request, evaluate
    from qor.policy.parser import parse_file

    request_path = Path(args.request)
    if not request_path.exists():
        print(f"Request file not found: {request_path}", file=sys.stderr)
        return 1

    data = json.loads(request_path.read_text(encoding="utf-8"))
    request = Request(
        principal=EntityUID(
            type=data["principal"]["type"],
            id=data["principal"]["id"],
        ),
        action=EntityUID(
            type=data["action"]["type"],
            id=data["action"]["id"],
        ),
        resource=EntityUID(
            type=data["resource"]["type"],
            id=data["resource"]["id"],
        ),
        context=data.get("context", {}),
    )
    entities = data.get("entities", {})

    # Load policies from qor/policies/*.cedar
    from qor import resources as _resources
    policies_dir = Path(str(_resources.asset("policies")))
    all_policies = []
    if policies_dir.exists():
        for cedar_file in sorted(policies_dir.glob("*.cedar")):
            all_policies.extend(parse_file(cedar_file))

    result = evaluate(request, all_policies, entities=entities)
    print(json.dumps({
        "decision": result.decision.value,
        "matching_policies": result.matching_policies,
    }, indent=2))
    return 0 if result.decision == Decision.ALLOW else 2
