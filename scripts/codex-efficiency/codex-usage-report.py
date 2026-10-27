#!/usr/bin/env python3
"""Summarize local Codex token metadata without printing conversation content."""

import argparse
import json
import os
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

# Credit-equivalent estimates, Standard speed, checked 2026-10-26.
# These are not charges for usage included in a ChatGPT subscription.
CREDIT_RATES = {
    "gpt-6-luna": (2.5, 0.25, 12.5),
    "gpt-6-sol": (50, 5, 250),
    "gpt-6.1-sol": (50, 2.5, 250),
    "gpt-6-astra": (250, 25, 1250),
}
USAGE_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens")


def codex_home():
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def workspace_name(cwd):
    parts = Path(cwd).parts
    if "GoProjects" not in parts:
        return "other"
    i = parts.index("GoProjects") + 1
    if i >= len(parts):
        return "other"
    if parts[i] == "worktrees" and i + 2 < len(parts):
        return parts[i + 2]
    return parts[i]


def summarize(path):
    contexts = {}
    records = []
    for line in path.open(errors="replace"):
        # Ignore chat messages, tool output, and other transcript records.
        if '"type":"turn_context"' not in line and '"type":"token_usage_record"' not in line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload = event.get("payload") or {}
        if event.get("type") == "turn_context":
            contexts[payload.get("turn_id")] = (
                workspace_name(payload.get("cwd") or ""),
                payload.get("model") or "unknown",
            )
        elif event.get("type") == "token_usage_record":
            usage = payload.get("usage") or {}
            records.append((payload.get("turn_id"), usage))
    totals = defaultdict(lambda: [0, 0, 0, 0])
    for turn_id, usage in records:
        workspace, model = contexts.get(turn_id, ("unknown", "unknown"))
        row = totals[(workspace, model)]
        for i, field in enumerate(USAGE_FIELDS):
            row[i] += int(usage.get(field) or 0)
        row[3] += 1
    return totals


def credits(input_tokens, cached_tokens, output_tokens, model):
    rates = CREDIT_RATES.get(model)
    if rates is None:
        return None
    uncached = max(0, input_tokens - cached_tokens)
    return (uncached * rates[0] + cached_tokens * rates[1] + output_tokens * rates[2]) / 1_000_000


def files_between(sessions_dir, start, end):
    for path in sessions_dir.rglob("*.jsonl"):
        try:
            day = date.fromisoformat(path.name[len("rollout-"):len("rollout-") + 10])
        except ValueError:
            continue
        if start <= day and (end is None or day < end):
            yield path


def collect(sessions_dir, start, end=None):
    totals = defaultdict(lambda: [0, 0, 0, 0])
    files = 0
    for path in files_between(sessions_dir, start, end):
        files += 1
        for key, values in summarize(path).items():
            row = totals[key]
            for i, value in enumerate(values):
                row[i] += value
    return files, totals


def weekly_summary(files, totals):
    input_tokens = cached_tokens = output_tokens = calls = unknown_calls = 0
    credit_equivalent = 0.0
    for (_, model), (input_count, cached_count, output_count, call_count) in totals.items():
        input_tokens += input_count
        cached_tokens += cached_count
        output_tokens += output_count
        calls += call_count
        estimate = credits(input_count, cached_count, output_count, model)
        if estimate is None:
            unknown_calls += call_count
        else:
            credit_equivalent += estimate
    return {
        "sessions": files,
        "calls": calls,
        "input": input_tokens,
        "uncached": input_tokens - cached_tokens,
        "output": output_tokens,
        "calls_per_session": calls / files if files else 0,
        "uncached_per_call": (input_tokens - cached_tokens) / calls if calls else 0,
        "output_per_call": output_tokens / calls if calls else 0,
        "cache_share": 100 * cached_tokens / input_tokens if input_tokens else 0,
        "credit_equiv": credit_equivalent,
        "known_credit_per_call": credit_equivalent / (calls - unknown_calls) if calls > unknown_calls else 0,
        "unknown_calls": unknown_calls,
    }


def configured_speed_tier():
    """Read only the root service_tier setting, without displaying other config data."""
    path = codex_home() / "config.toml"
    if not path.exists():
        return "unset"
    section = ""
    try:
        for line in path.open(errors="replace"):
            value = line.strip()
            if value.startswith("["):
                section = value
            elif not section and value.startswith("service_tier") and "=" in value:
                return value.split("=", 1)[1].split("#", 1)[0].strip().strip('"\'')
    except OSError:
        return "unreadable"
    return "unset"


def weekly_report(sessions_dir, today):
    this_monday = today - timedelta(days=today.weekday())
    last_monday = this_monday - timedelta(days=7)
    prior_monday = last_monday - timedelta(days=7)
    prior_files, prior_totals = collect(sessions_dir, prior_monday, last_monday)
    last_files, last_totals = collect(sessions_dir, last_monday, this_monday)
    prior = weekly_summary(prior_files, prior_totals)
    last = weekly_summary(last_files, last_totals)
    print(f"Completed weeks by session start date: {prior_monday}–{last_monday - timedelta(days=1)} vs {last_monday}–{this_monday - timedelta(days=1)}")
    print(f"{'Measure':22} {'Prior week':>15} {'Last week':>15} {'Change':>10}")
    for label, key, fmt in [
        ("Session files", "sessions", ",d"),
        ("Model calls", "calls", ",d"),
        ("Input tokens", "input", ",d"),
        ("Uncached input", "uncached", ",d"),
        ("Output tokens", "output", ",d"),
        ("Calls per session", "calls_per_session", ".1f"),
        ("Uncached per call", "uncached_per_call", ",.0f"),
        ("Output per call", "output_per_call", ",.0f"),
        ("Cached input share", "cache_share", ".1f"),
        ("Known credit-equiv", "credit_equiv", ".2f"),
        ("Credit-equiv/call", "known_credit_per_call", ".2f"),
        ("Unestimated calls", "unknown_calls", ",d"),
    ]:
        old, new = prior[key], last[key]
        change = f"{(new / old - 1) * 100:+.1f}%" if old else "n/a"
        suffix = "%" if key == "cache_share" else ""
        print(f"{label:22} {format(old, fmt) + suffix:>15} {format(new, fmt) + suffix:>15} {change:>10}")
    print("\nLast completed week by model:")
    by_model = defaultdict(lambda: [0, 0, 0, 0])
    for (_, model), values in last_totals.items():
        for i, value in enumerate(values):
            by_model[model][i] += value
    for model, (input_count, cached_count, output_count, call_count) in sorted(by_model.items()):
        estimate = credits(input_count, cached_count, output_count, model)
        display = f"{estimate:.2f}" if estimate is not None else "unestimated"
        print(f"  {model}: {call_count:,} calls, {input_count - cached_count:,} uncached input, {display} Standard credit-equiv")
    print("\nChecks:")
    override = codex_home() / "AGENTS.override.md"
    print(f"  Instruction override: {'present' if override.exists() else 'missing'}" + (f" ({override.stat().st_size:,} bytes)" if override.exists() else ""))
    print(f"  Unestimated model calls: {last['unknown_calls']:,}; credit-equivalent excludes these calls.")
    print(f"  Configured service tier: {configured_speed_tier()}; verify actual tier and charges in your usage dashboard.")
    print("  Quality: review accepted tasks and repair time separately; local token logs cannot measure them.")
    print("  Trend: compare workload and model mix before treating a usage change as an efficiency change.")
    print("Standard credit-equivalent excludes speed tiers and contract terms; it is not your bill or included-plan usage.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", type=date.fromisoformat, default=date.today() - timedelta(days=6))
    parser.add_argument("--until", type=date.fromisoformat, help="Exclusive end date for a custom range")
    parser.add_argument("--weekly", action="store_true", help="Compare the last two completed Monday–Sunday weeks")
    parser.add_argument("--sessions-dir", type=Path, default=codex_home() / "sessions")
    args = parser.parse_args()
    if args.weekly:
        weekly_report(args.sessions_dir, date.today())
        return
    if args.until is not None and args.until <= args.since:
        parser.error("--until must be after --since")
    files, totals = collect(args.sessions_dir, args.since, args.until)
    period = f"{args.since} to {args.until} (exclusive)" if args.until else f"since {args.since}"
    print(f"Period {period}: {files} session files; model calls are counted from usage metadata.")
    print("Workspace           Model             Input       Cached      Output      Calls   Credit-equiv")
    for (workspace, model), (input_tokens, cached_tokens, output_tokens, calls) in sorted(totals.items()):
        estimate = credits(input_tokens, cached_tokens, output_tokens, model)
        display = f"{estimate:.2f}" if estimate is not None else "n/a"
        print(f"{workspace[:19]:19} {model[:17]:17} {input_tokens:11,d} {cached_tokens:11,d} {output_tokens:11,d} {calls:9,d} {display:>14}")
    print("Credit-equiv uses the 2026-10-26 Standard rate card. It excludes speed tiers and contract terms; it is not your bill or included-plan usage.")


if __name__ == "__main__":
    main()
