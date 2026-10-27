# Codex working instructions

Installed by `copilot-prompts/scripts/install.sh --codex-efficiency`. Keep any generated `AGENTS.md` intact. Follow the current repository's `AGENTS.md` and load linked guidance only when the task calls for it.

## Work across repositories

- Follow repository instructions for coding conventions, tests, data handling, and release rules.
- Keep context focused: read the files and guidance needed for the task, and summarize large tool results.
- Before committing or pushing, show the changed files and a proposed one-line commit message and wait for approval. Never amend a pushed commit. After approval, commit and push together. Read `$CODEX_HOME/guidance/git-push.instructions.md` and `$CODEX_HOME/guidance/git-commits.instructions.md` when relevant.
- Before posting a PR comment, show the draft and wait for approval. Read `$CODEX_HOME/guidance/pr-comments.instructions.md` when relevant.
- For Go implementation, read `$CODEX_HOME/guidance/go-standards.instructions.md`.

## Build only what the task needs

For each task, use this scope check without adding a separate planning turn for routine work:
1. Identify the current outcome and how to verify it.
2. Reuse existing code and tools; make the smallest change that satisfies the current requirements, including necessary tests and safety checks.
3. Add an abstraction, automation, agent handoff, or report only when a current requirement, concrete risk, or observed repeated friction justifies it. Name that reason when adding one.
4. Once the outcome is verified, stop. Leave speculative improvements unbuilt; note one briefly only if it will help later.

## Agent-driven routing

For each coding task, decide whether to complete it directly or delegate one bounded, independent part. Prefer direct work for short or sequential tasks. Use `cost_explorer` for focused codebase searches that can return a concise file-and-symbol map. Use `quality_reviewer` after implementation when correctness, data handling, concurrency, or contract changes warrant independent review. Spawn at most two specialists at once; do not duplicate the same investigation. Choose the least costly role likely to meet the task's quality bar, then verify the result yourself. Mention the routing choice and any remaining uncertainty in the final report.
