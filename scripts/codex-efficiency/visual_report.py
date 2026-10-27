#!/usr/bin/env python3
"""Create a self-contained, local Codex usage dashboard from session metadata."""
import argparse
import csv
import html
import importlib.util
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("usage", HERE / "codex-usage-report.py")
usage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usage)


def profile_output():
    suffix = "latest.html" if usage.codex_home() == Path.home() / ".codex" else f"{usage.codex_home().name.lstrip('.')}-latest.html"
    return HERE / "reports" / suffix


def number(value):
    return f"{value:,.0f}"


def delta(before, after):
    return "—" if not before else f"{(after / before - 1) * 100:+.1f}%"


def model_data(totals):
    rows = defaultdict(lambda: [0, 0, 0, 0])
    for (_, model), values in totals.items():
        for i, value in enumerate(values):
            rows[model][i] += value
    return sorted(rows.items(), key=lambda item: item[1][0] - item[1][1], reverse=True)


def load_outcomes(path):
    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        required = {"week_start", "accepted_tasks", "repair_minutes"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"{path}: expected columns {', '.join(sorted(required))}")
        outcomes = {}
        for row in reader:
            start = date.fromisoformat(row["week_start"])
            accepted = int(row["accepted_tasks"])
            repair = float(row["repair_minutes"])
            if start.weekday() != 0 or accepted < 0 or repair < 0 or start in outcomes:
                raise ValueError(f"{path}: invalid or duplicate week {start}")
            outcomes[start] = (accepted, repair)
        return outcomes


def render(sessions_dir, today, outcomes_path=None):
    this_monday = today - timedelta(days=today.weekday())
    last_monday = this_monday - timedelta(days=7)
    prior_monday = last_monday - timedelta(days=7)
    outcomes = load_outcomes(outcomes_path) if outcomes_path else {}
    weeks = []
    for offset in range(8, 0, -1):
        start = this_monday - timedelta(days=7 * offset)
        files, totals = usage.collect(sessions_dir, start, start + timedelta(days=7))
        weeks.append((start, usage.weekly_summary(files, totals), totals))
    _, prior, _ = weeks[-2]
    _, last, lt = weeks[-1]
    rows = model_data(lt)
    max_uncached = max((v[0] - v[1] for _, v in rows), default=1) or 1
    model_rows = []
    for model, (inp, cached, out, calls) in rows:
        uncached = max(0, inp - cached)
        est = usage.credits(inp, cached, out, model)
        width = max(1, round(100 * uncached / max_uncached))
        model_rows.append(f'<tr><th scope="row">{html.escape(model)}</th><td><div class="bar" style="width:{width}%"></div></td><td>{number(uncached)}</td><td>{number(calls)}</td><td>{f"{est:,.1f}" if est is not None else "Unestimated"}</td></tr>')
    measures = [
        ("Uncached input", "uncached", "tokens"),
        ("Cached input", "cached", "tokens"),
        ("Output", "output", "tokens"),
        ("Model calls", "calls", "calls"),
        ("Uncached / call", "uncached_per_call", "tokens"),
        ("Credit equiv. / known call", "known_credit_per_call", "credits"),
    ]
    metric_rows = []
    for label, key, unit in measures:
        before = prior["input"] - prior["uncached"] if key == "cached" else prior[key]
        after = last["input"] - last["uncached"] if key == "cached" else last[key]
        display_before = f"{before:,.2f}" if key == "known_credit_per_call" else number(before)
        display_after = f"{after:,.2f}" if key == "known_credit_per_call" else number(after)
        metric_rows.append(f'<tr><th scope="row">{label}</th><td>{display_before}</td><td>{display_after}</td><td>{delta(before, after)}</td><td>{unit}</td></tr>')
    prior_total = prior["uncached"] + prior["output"]
    last_total = last["uncached"] + last["output"]
    known_coverage = 100 * (last["calls"] - last["unknown_calls"]) / last["calls"] if last["calls"] else 0
    tier = html.escape(usage.configured_speed_tier())
    profile = html.escape(usage.codex_home().name)
    trend_rows = []
    measured_weeks = sum(start in outcomes for start, _, _ in weeks)
    outcome_note = (f"{measured_weeks} of 8 weeks have accepted-task outcomes. "
                    "Compare per-task figures only when each count covers all work in that profile and week."
                    if measured_weeks else "No accepted-task outcomes recorded yet. The token trend alone cannot show whether work became more cost effective.")
    for start, week, _ in weeks:
        coverage = 100 * (week["calls"] - week["unknown_calls"]) / week["calls"] if week["calls"] else 0
        accepted, repair = outcomes.get(start, (None, None))
        work_tokens = week["uncached"] + week["output"]
        per_task = number(work_tokens / accepted) if accepted else "—"
        credit_per_task = f'{week["credit_equiv"] / accepted:,.1f}' if accepted and coverage == 100 else "—"
        accepted_display = number(accepted) if accepted is not None else "—"
        repair_display = f"{repair:,.0f}" if repair is not None else "—"
        trend_rows.append(f'<tr><th scope="row">{start} – {start + timedelta(days=6)}</th><td>{number(week["uncached"])}</td><td>{number(week["calls"])}</td><td>{accepted_display}</td><td>{per_task}</td><td>{credit_per_task}</td><td>{repair_display}</td><td>{coverage:.0f}%</td></tr>')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Codex usage • week ending {this_monday-timedelta(days=1)}</title><link rel="icon" href="data:,">
<style>
:root{{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#152329;background:#f4f7f7}}*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:1120px;margin:auto;padding:36px 22px 64px}}header{{border-bottom:2px solid #152329;padding-bottom:22px;display:flex;justify-content:space-between;gap:20px;align-items:end}}h1{{font-size:clamp(2rem,4vw,3.3rem);letter-spacing:-.05em;margin:0}}h2{{font-size:1.35rem;letter-spacing:-.03em;margin:0 0 14px}}p{{line-height:1.5}}.eyebrow{{text-transform:uppercase;letter-spacing:.14em;font-size:.75rem;font-weight:800;color:#367469;margin:0 0 8px}}.muted{{color:#53666a}}.period{{text-align:right;font-weight:650}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:24px 0}}.card,.panel{{background:white;border:1px solid #d7e2e1;border-radius:14px}}.card{{padding:20px}}.card .value{{font-size:clamp(1.8rem,3vw,2.8rem);font-weight:800;letter-spacing:-.05em;margin:8px 0 0}}.card .change{{font-weight:700;color:#8b4a22}}.card .label{{color:#53666a;font-size:.9rem}}.panel{{padding:22px;margin:16px 0}}.callout{{border-left:4px solid #d99045;background:#fff8ed;padding:14px 18px;border-radius:0 9px 9px 0;margin:18px 0}}table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{text-align:right;padding:11px 8px;border-bottom:1px solid #e5ebea}}th:first-child,td:first-child{{text-align:left}}thead th{{color:#53666a;font-size:.75rem;text-transform:uppercase;letter-spacing:.06em}}tbody th{{font-weight:600}}.bar{{height:12px;background:#2e8976;border-radius:3px;min-width:2px}}.model td:nth-child(2){{width:30%}}a{{color:#176e5e}}ul{{line-height:1.65;padding-left:20px}}.small{{font-size:.82rem;color:#53666a}}.tag{{display:inline-block;background:#e8f3ee;color:#176e5e;border-radius:5px;padding:3px 7px;font-weight:700}}@media(max-width:700px){{header{{display:block}}.period{{text-align:left}}.grid{{grid-template-columns:1fr}}.scroll{{overflow-x:auto}}table{{min-width:610px}}}}@media print{{body{{background:white}}main{{max-width:none;padding:0}}.card,.panel{{break-inside:avoid}}a{{color:inherit}}}}
</style></head><body><main><header><div><p class="eyebrow">Local usage intelligence</p><h1>Codex usage</h1><p class="muted">A weekly trend of token use and cost proxies.</p></div><div class="period">Profile: {profile}<br>Last completed week<br>{last_monday} – {this_monday-timedelta(days=1)}<br><span class="small">Compared with {prior_monday} – {last_monday-timedelta(days=1)}</span></div></header>
<div class="grid"><div class="card"><div class="label">Uncached input</div><div class="value">{last['uncached']/1e6:,.1f}M</div><div class="change">{delta(prior['uncached'],last['uncached'])} week over week</div></div><div class="card"><div class="label">Uncached input per call</div><div class="value">{number(last['uncached_per_call'])}</div><div class="change">{delta(prior['uncached_per_call'],last['uncached_per_call'])} week over week</div></div><div class="card"><div class="label">Estimated call coverage</div><div class="value">{known_coverage:.0f}%</div><div class="small">{number(last['unknown_calls'])} calls use models without a rate here</div></div></div>
<div class="callout"><strong>Cost setting:</strong> Configured service tier is <strong>{tier}</strong>. Check your usage dashboard for the tier actually used; Fast mode may consume included limits faster or cost more in credits. <a href="https://learn.chatgpt.com/docs/agent-configuration/speed">OpenAI speed guidance</a>.</div><div class="callout"><strong>Interpretation:</strong> This is a workload view, not proof of savings. Session volume, task mix, model choice, and retries can change the total. Compare completed tasks of similar scope and quality before claiming cost effectiveness.</div>
<section class="panel"><h2>Eight completed weeks</h2><p class="muted">{outcome_note}</p><div class="scroll"><table><thead><tr><th>Week</th><th>Uncached input</th><th>Calls</th><th>Accepted tasks</th><th>Tokens / accepted</th><th>Std credits / accepted</th><th>Repair min</th><th>Rated calls</th></tr></thead><tbody>{''.join(trend_rows)}</tbody></table></div><p class="small">Tokens / accepted = uncached input + output across all calls divided by accepted tasks. Count every accepted task represented by this profile and week; leave the CSV row out if the count is incomplete. Standard credit equivalents appear only when all model calls have a rate. Neither figure is your bill. Record outcomes in the current CODEX_HOME as codex-efficiency-outcomes.csv; use the bundled outcomes.example.csv as a template.</p></section>
<section class="panel"><h2>Week over week</h2><div class="scroll"><table><thead><tr><th>Measure</th><th>Prior week</th><th>Last week</th><th>Change</th><th>Unit</th></tr></thead><tbody>{''.join(metric_rows)}</tbody></table></div><p class="small">Input includes cached input. The total of uncached input and output was {number(prior_total)} versus {number(last_total)} tokens. This total is descriptive; it is not a billing unit.</p></section>
<section class="panel"><h2>Last week by model</h2><div class="scroll"><table class="model"><thead><tr><th>Model</th><th>Relative uncached input</th><th>Uncached input</th><th>Calls</th><th>Standard credit equiv.</th></tr></thead><tbody>{''.join(model_rows) or '<tr><td colspan="5">No session records found.</td></tr>'}</tbody></table></div><p class="small">Bars are scaled to the largest model, not to all usage. Credit equivalents use the bundled Standard rate card for known models only. They are not dollars, your bill, or included-plan usage.</p></section>
<section class="panel"><h2>What to check each week</h2><ul><li><strong>Effectiveness:</strong> Record accepted tasks, retries, and repair time alongside these token trends. Without them, cost per accepted task is unknown.</li><li><strong>Routing:</strong> Check whether a bounded explorer or reviewer saved enough main-agent work to cover its own calls and any repair work.</li><li><strong>Quality:</strong> Record accepted tasks, review findings, regressions, and repair time. These are not in local token logs.</li><li><strong>Actual spend:</strong> Check the Codex usage dashboard for your plan's allowance and applicable charges.</li><li><strong>Context:</strong> Revisit broad always-loaded instructions and enabled MCP servers when token growth has no workload explanation.</li></ul></section>
<footer class="small">Generated {today}. Reads local session token metadata only; does not embed prompts or transcripts. Weeks follow session start dates. Use the browser Print command to save this page as PDF.</footer></main></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-dir", type=Path, default=usage.codex_home() / "sessions")
    parser.add_argument("--output", type=Path, default=profile_output())
    parser.add_argument("--today", type=date.fromisoformat, default=date.today(), help="Date override for repeatable reports")
    parser.add_argument("--outcomes", type=Path, default=usage.codex_home() / "codex-efficiency-outcomes.csv", help="Local weekly accepted-task and repair-time CSV")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(args.sessions_dir, args.today, args.outcomes), encoding="utf-8")
    print(args.output.resolve())

if __name__ == "__main__":
    main()
