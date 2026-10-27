#!/usr/bin/env python3
"""Install Codex efficiency tools from the copilot-prompts repository."""
import argparse
import shutil
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GUIDANCE = ("git-push", "git-commits", "pr-comments", "go-standards")


def backup(path):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    saved = path.with_name(path.name + ".backup-" + stamp)
    shutil.copy2(path, saved, follow_symlinks=False)
    print(f"backup: {saved}")


def install(home, apply, report_only, codex_home=None, check=False):
    home = home.expanduser()
    codex_home = (codex_home or home / ".codex").expanduser()
    default_home = (home / ".codex").resolve()
    if codex_home.resolve() == default_home and not report_only:
        existing_override = codex_home / "AGENTS.override.md"
        general_source = HERE / "AGENTS.override.md"
        if existing_override.exists() or existing_override.is_symlink():
            if not existing_override.is_file() or existing_override.read_bytes() != general_source.read_bytes():
                raise SystemExit(
                    "Default Codex home already has different global instructions. "
                    "Use --codex-home for a separate profile or review the existing override before replacing it."
                )
        else:
            existing_base = codex_home / "AGENTS.md"
            if existing_base.is_symlink() or (existing_base.is_file() and existing_base.stat().st_size):
                raise SystemExit(
                    "Default Codex home already has AGENTS.md; a new override would hide it. "
                    "Use --codex-home for a separate profile or review the existing instructions first."
                )
    shared = home / ".local/share/codex-efficiency"
    copies = [
        (HERE / "codex-usage-report.py", shared / "codex-usage-report.py"),
        (HERE / "visual_report.py", shared / "visual_report.py"),
        (HERE / "IMPROVEMENT-REPORT.html", shared / "IMPROVEMENT-REPORT.html"),
        (HERE / "STRATEGY-REVIEW.md", shared / "STRATEGY-REVIEW.md"),
        (HERE / "outcomes.example.csv", shared / "outcomes.example.csv"),
    ]
    links = []
    if not report_only:
        copies += [
            (HERE / "AGENTS.override.md", codex_home / "AGENTS.override.md"),
            (HERE / "agents/cost_explorer.toml", codex_home / "agents/cost_explorer.toml"),
            (HERE / "agents/quality_reviewer.toml", codex_home / "agents/quality_reviewer.toml"),
        ]
        links = [
            (REPO / "instructions" / "core" / f"{name}.instructions.md",
             codex_home / "guidance" / f"{name}.instructions.md")
            for name in GUIDANCE
        ]
    missing = [str(source) for source, _ in copies + links if not source.is_file()]
    if missing:
        raise SystemExit("Missing kit source files: " + ", ".join(missing))
    if check:
        print("Codex efficiency preflight okay.")
        return
    for source, target in copies:
        same = target.is_file() and not target.is_symlink() and target.read_bytes() == source.read_bytes()
        print(f"{'current' if same else 'install'}: {target}")
        if apply and not same:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                backup(target)
                if target.is_symlink():
                    target.unlink()
            shutil.copy2(source, target)
    for source, target in links:
        same = target.is_symlink() and target.resolve() == source.resolve()
        print(f"{'current' if same else 'link'}: {target}")
        if apply and not same:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                backup(target)
                target.unlink()
            target.symlink_to(source)
    if not apply:
        print("Preview only. Re-run with --apply to install.")
    else:
        print("Report tools installed; Codex instructions unchanged." if report_only else "Installed. Start a new Codex chat to load the routing instructions.")
        print(f"Codex home: {codex_home}")
        print(f"Weekly HTML: CODEX_HOME={codex_home} python3 {shared / 'visual_report.py'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Install after previewing destinations")
    parser.add_argument("--check", action="store_true", help="Validate destinations and sources without installing")
    parser.add_argument("--report-only", action="store_true", help="Install reports without Codex instructions or roles")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Override user home directory for testing")
    parser.add_argument("--codex-home", type=Path, help="Codex home destination; defaults to ~/.codex")
    args = parser.parse_args()
    install(args.home, args.apply, args.report_only, args.codex_home, args.check)

if __name__ == "__main__":
    main()
