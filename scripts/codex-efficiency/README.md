# Codex efficiency tools

These tools add a separate improvement report, a local weekly usage dashboard, and two optional Codex specialist roles to the `copilot-prompts` setup. The short `AGENTS.override.md` keeps the always-loaded instructions smaller; task guidance is linked from this repository and read when relevant. This is an opt-in Codex setup. It does not change the VS Code Copilot profiles.

## Install on each machine

On a clean machine, run this from the repository root:

```sh
./scripts/install.sh --codex-efficiency
```

This installs the core Copilot prompts plus the organization-neutral Codex instructions and optional specialist roles in the default `~/.codex`. It also copies the improvement report and weekly dashboard tools into `~/.local/share/codex-efficiency/`. Repository `AGENTS.md` files still apply to their own repositories.

For an existing organization-specific Codex profile, install only the reporting tools so its instructions remain in place:

```sh
python3 scripts/codex-efficiency/install.py --report-only --apply
```

The portable kit contains only generic instructions. Keep organization-specific policies in the corresponding repository or managed Codex profile.

If the default `~/.codex` already has different global instructions in `AGENTS.override.md` or a nonempty `AGENTS.md`, the generic installer stops before masking them. Use the Codex-only installer with a different home for a second profile:

```sh
python3 scripts/codex-efficiency/install.py --codex-home "$HOME/.codex-personal" --apply
```

Launch VS Code with `CODEX_HOME` set to that profile before starting Codex. Quit an existing VS Code process first so the new process receives the environment:

```sh
CODEX_HOME="$HOME/.codex-personal" code --new-window /path/to/repo
```

A separate Codex home has separate configuration, authentication, skills, sessions, and outcomes, so it may require sign-in. The installer does not copy those files. To work in two homes simultaneously in VS Code, use separate editor processes; opening another workspace in the same process does not change its environment. Codex supports `CODEX_HOME` in the IDE extension and CLI.

The installer backs up different destination files before replacing them. It leaves existing `AGENTS.md`, `config.toml`, session logs, and repository instructions alone. Start a new Codex chat after installation. The named models must be available to your account.

To preview Codex-specific changes, run `python3 scripts/codex-efficiency/install.py`. Add `--apply` to install. Use `--report-only --apply` for reports alone. Python 3.11 or newer is recommended.

## The repeatable work loop

The installed Codex instructions use four checks for every task: define the outcome and verification, reuse what exists, add extra structure only for a current need or observed friction, then stop after verification. This is a scope rule, not an extra ceremony. A reviewer is still useful when the change has material correctness, data, concurrency, or contract risk. Revisit a deferred idea when a later task supplies evidence that it is needed.

## Improvement report

Open `~/.local/share/codex-efficiency/IMPROVEMENT-REPORT.html` or print it to PDF. It compares published strategies across providers, explains this setup, and defines the benchmark needed to judge savings. The detailed source review is in `STRATEGY-REVIEW.md` beside it.

## Weekly dashboard

```sh
python3 ~/.local/share/codex-efficiency/visual_report.py
python3 ~/.local/share/codex-efficiency/codex-usage-report.py --weekly
```

With the default Codex home, the first command writes `~/.local/share/codex-efficiency/reports/latest.html`; with `CODEX_HOME=~/.codex-personal`, it writes `reports/codex-personal-latest.html`. Open it in a browser or print it to PDF. It shows eight completed Monday–Sunday weeks and a detailed comparison of the last two on that machine. Nothing is uploaded. No session logs, prompts, or credentials are included in the HTML.

To see cost proxies per accepted task, copy `~/.local/share/codex-efficiency/outcomes.example.csv` to `$CODEX_HOME/codex-efficiency-outcomes.csv` (or `~/.codex/codex-efficiency-outcomes.csv` when `CODEX_HOME` is unset) and add one Monday-start row per completed week. `accepted_tasks` must count every delivered task represented by that profile's session logs for that week; leave the row out if the count is incomplete. `repair_minutes` is human time spent fixing those tasks. The CSV stays local and the installer does not overwrite it. Until it exists, the dashboard explicitly marks effectiveness as unmeasured. Check review findings and actual charges separately. Local token logs cannot establish work quality, actual plan charges, or whether the two specialist roles saved money overall. The report's credit equivalents use bundled Standard rates only for known models. Verify your actual usage and service tier in the Codex usage dashboard, especially if `service_tier` is set to `priority` or `fast`.

For the wider comparison across Anthropic, Google, GitHub, Databricks, and academic research, see the separate [improvement report](IMPROVEMENT-REPORT.html) and [strategy review](STRATEGY-REVIEW.md).

Sources: [Codex instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [CODEX_HOME environment support](https://learn.chatgpt.com/docs/config-file/environment-variables), [OpenAI pricing and usage](https://learn.chatgpt.com/docs/pricing), [shorter skills and AGENTS.md](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), [multi-agent guidance](https://developers.openai.com/api/docs/guides/agents-api/multi-agent), [speed modes](https://learn.chatgpt.com/docs/agent-configuration/speed).
