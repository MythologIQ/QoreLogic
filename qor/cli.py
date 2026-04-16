"""QorLogic CLI -- agent-agnostic skill distribution harness."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

__version__ = "0.14.0"


def _default_dist_root() -> Path:
    from qor import resources as _resources
    return Path(str(_resources.asset("dist")))


def _do_install(
    host: str,
    target_override: Path | None = None,
    dist_root: Path | None = None,
    dry_run: bool = False,
) -> int:
    """Install compiled variants into a host target directory."""
    from qor.hosts import resolve

    target = resolve(host, target_override=target_override)
    if dist_root is None:
        dist_root = _default_dist_root()

    manifest_path = dist_root / "manifest.json"
    if not manifest_path.exists():
        print("No manifest.json found. Run 'qorlogic compile' first.", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    claude_root = dist_root / "variants" / "claude"
    installed = []

    for entry in manifest["files"]:
        rel = entry["install_rel_path"]
        src = claude_root / rel
        if not src.exists():
            continue

        if rel.startswith("skills/"):
            dst = target.skills_dir / rel[len("skills/"):]
        elif rel.startswith("agents/"):
            dst = target.agents_dir / rel[len("agents/"):]
        else:
            continue

        if dry_run:
            print(f"  [dry-run] {src} -> {dst}")
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        installed.append({"path": str(dst), "sha256": entry["sha256"]})

    if not dry_run and installed:
        record_path = (target_override or target.skills_dir.parent) / ".qorlogic-installed.json"
        record_path.write_text(
            json.dumps({"files": installed}, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Installed {len(installed)} files to {target.name}")
    elif dry_run:
        print(f"[dry-run] Would install {len(manifest['files'])} files to {target.name}")

    return 0


def _do_uninstall(
    host: str = "claude",
    target_override: Path | None = None,
) -> int:
    """Remove previously installed files using the install record."""
    base = target_override
    if base is None:
        from qor.hosts import resolve
        target = resolve(host)
        base = target.skills_dir.parent

    record_path = base / ".qorlogic-installed.json"
    if not record_path.exists():
        print("No install record found.", file=sys.stderr)
        return 1

    data = json.loads(record_path.read_text(encoding="utf-8"))
    removed = 0
    for entry in data["files"]:
        p = Path(entry["path"])
        if p.exists():
            p.unlink()
            removed += 1
            # Clean empty parent dirs
            parent = p.parent
            while parent != base and parent.exists():
                try:
                    parent.rmdir()
                    parent = parent.parent
                except OSError:
                    break

    record_path.unlink()
    print(f"Removed {removed} files")
    return 0


def _do_list(args: argparse.Namespace) -> int:
    """List available or installed skills."""
    if getattr(args, "available", False):
        dist_root = _default_dist_root()
        manifest_path = dist_root / "manifest.json"
        if not manifest_path.exists():
            print("No manifest. Run 'qorlogic compile' first.", file=sys.stderr)
            return 1
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        seen = set()
        for entry in data["files"]:
            sid = entry["id"]
            if sid not in seen:
                print(sid)
                seen.add(sid)
        return 0

    if getattr(args, "installed", False):
        host = getattr(args, "host", "claude")
        from qor.hosts import resolve
        target = resolve(host)
        record = target.skills_dir.parent / ".qorlogic-installed.json"
        if not record.exists():
            print("No install record found.", file=sys.stderr)
            return 1
        data = json.loads(record.read_text(encoding="utf-8"))
        for entry in data["files"]:
            print(entry["path"])
        return 0

    print("Specify --available or --installed", file=sys.stderr)
    return 1


def _do_info(args: argparse.Namespace) -> int:
    """Show skill metadata from compiled variants."""
    skill_name = args.skill
    dist_root = _default_dist_root()
    skill_md = dist_root / "variants" / "claude" / "skills" / skill_name / "SKILL.md"
    if not skill_md.exists():
        # Try as loose skill
        skill_md = dist_root / "variants" / "claude" / "skills" / f"{skill_name}.md"
    if not skill_md.exists():
        print(f"Skill {skill_name!r} not found", file=sys.stderr)
        return 1
    print(skill_md.read_text(encoding="utf-8")[:500])
    return 0


def _do_compile(args: argparse.Namespace) -> int:
    """Compile variants from source."""
    from qor.scripts import dist_compile
    summary = dist_compile.compile_all(
        dist_compile.DEFAULT_OUT, dry_run=getattr(args, "dry_run", False),
    )
    action = "Would emit" if getattr(args, "dry_run", False) else "Compiled"
    print(f"{action}: {summary['skill_dirs']} skill dirs, {summary['loose_skills']} loose, {summary['agents']} agents")
    return 0


def _compute_coverage(practice_map: dict[int, list[str]]) -> tuple[int, int, int]:
    """Compute (group_count, unique_practices, total_tags) from practice_map."""
    all_practices: set[str] = set()
    total = 0
    for practices in practice_map.values():
        for p in practices:
            all_practices.add(p)
            total += 1
    groups = {p.split(".")[0] for p in all_practices}
    return len(groups), len(all_practices), total


def _do_compliance_report(
    ledger_path: Path | None = None,
) -> str:
    """Generate SSDF practice coverage report from ledger."""
    from qor.scripts.ledger_hash import extract_ssdf_practices
    if ledger_path is None:
        from qor import workdir
        ledger_path = workdir.meta_ledger()
    practice_map = extract_ssdf_practices(ledger_path)
    if not practice_map:
        return "No SSDF practice tags found in ledger. Coverage: 0"

    # Aggregate by practice
    by_practice: dict[str, list[int]] = {}
    for entry_num, practices in practice_map.items():
        for p in practices:
            by_practice.setdefault(p, []).append(entry_num)

    lines = ["SSDF Practice Coverage:"]
    for practice in sorted(by_practice):
        entries = by_practice[practice]
        entry_refs = ", ".join(f"Entry #{n}" for n in sorted(entries))
        lines.append(f"  {practice}: {len(entries)} entries ({entry_refs})")

    groups, unique, total = _compute_coverage(practice_map)
    lines.append(f"Coverage: {groups} practice groups, {unique} individual practices, {total} total tags")
    return "\n".join(lines)


def _do_verify_ledger(args: argparse.Namespace) -> int:
    """Verify META_LEDGER.md chain."""
    from qor.scripts import ledger_hash
    from qor import workdir
    ledger_path = workdir.meta_ledger()
    return ledger_hash.verify(ledger_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="qorlogic",
        description="S.H.I.E.L.D. governance skills for AI coding hosts.",
    )
    parser.add_argument(
        "--version", action="version", version=f"qorlogic {__version__}",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    _hosts = ["claude", "kilo-code", "codex"]
    sp_install = sub.add_parser("install", help="install skills into an AI coding host")
    sp_install.add_argument("--host", required=True, choices=_hosts)
    sp_install.add_argument("--target", type=Path, default=None)
    sp_install.add_argument("--dry-run", action="store_true")
    sp_uninstall = sub.add_parser("uninstall", help="remove installed skills")
    sp_uninstall.add_argument("--host", default="claude", choices=_hosts)
    sp_uninstall.add_argument("--target", type=Path, default=None)
    sp_list = sub.add_parser("list", help="enumerate available or installed skills")
    sp_list.add_argument("--available", action="store_true")
    sp_list.add_argument("--installed", action="store_true")
    sp_list.add_argument("--host", default="claude")
    sp_info = sub.add_parser("info", help="show skill metadata")
    sp_info.add_argument("skill", help="skill name")
    sp_compile = sub.add_parser("compile", help="regenerate variants from source")
    sp_compile.add_argument("--dry-run", action="store_true")
    sub.add_parser("verify-ledger", help="verify META_LEDGER.md chain")
    sp_init = sub.add_parser("init", help="initialize .qorlogic/config.json")
    sp_init.add_argument("--host", default="claude", choices=_hosts)
    sp_init.add_argument("--profile", default="sdlc", choices=["sdlc", "filesystem", "data", "research"])
    sp_init.add_argument("--target", type=Path, default=None)
    sp_compliance = sub.add_parser("compliance", help="NIST SSDF compliance reporting")
    compliance_sub = sp_compliance.add_subparsers(dest="compliance_command", metavar="<subcommand>")
    sp_compliance_report = compliance_sub.add_parser("report", help="show SSDF practice coverage")
    sp_compliance_report.add_argument("--ledger", type=Path, default=None)
    sp_policy = sub.add_parser("policy", help="policy engine commands")
    policy_sub = sp_policy.add_subparsers(dest="policy_command", metavar="<subcommand>")
    sp_policy_check = policy_sub.add_parser("check", help="evaluate request against cedar policies")
    sp_policy_check.add_argument("request", help="path to request JSON file")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    dispatch = {
        "install": lambda: _do_install(args.host, target_override=args.target, dry_run=args.dry_run),
        "uninstall": lambda: _do_uninstall(host=args.host, target_override=args.target),
        "list": lambda: _do_list(args),
        "info": lambda: _do_info(args),
        "compile": lambda: _do_compile(args),
        "verify-ledger": lambda: _do_verify_ledger(args),
    }
    if args.command in dispatch:
        return dispatch[args.command]()
    if args.command == "compliance":
        if getattr(args, "compliance_command", None) == "report":
            ledger = getattr(args, "ledger", None)
            print(_do_compliance_report(ledger_path=ledger))
            return 0
        sp_compliance.print_help()
        return 0
    if args.command == "init":
        from qor.cli_policy import do_init
        return do_init(args)
    if args.command == "policy":
        from qor.cli_policy import do_policy_check
        if getattr(args, "policy_command", None) == "check":
            return do_policy_check(args)
        sp_policy.print_help()
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
