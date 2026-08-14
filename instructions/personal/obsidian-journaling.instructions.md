---
applyTo: "**"
description: Automatically log engineering activity to Obsidian vault at key moments
---

# Obsidian Auto-Journaling

Vault path: `~/ObsidianVault/`

## When to write

### 1. Task start (`new-task.sh` runs)
- Check if `projects/<TICKET> *.md` exists in the vault
- If not, create it using this skeleton:

```markdown
# <TICKET> <Short Description>
#chathub #services

**Ticket**: https://everlong.atlassian.net/browse/<TICKET>
**Branch**: <branch-name>
**Status**: IN PROGRESS
**Repos**:

## Context


## Key PRs


## Decisions


## Learnings

```

- If it exists, update **Status** to `IN PROGRESS` and update **Branch** if changed

### 2. Commit proposed (before asking for confirmation)
- Append a bullet to today's daily note at `daily/<YYYY-MM-DD>.md`
- Create the daily note from template if it doesn't exist:

```markdown
# <YYYY-MM-DD>

## Plan

\`\`\`dataview
TASK
FROM #staff-track
WHERE !completed
GROUP BY file.link
\`\`\`

## Activity
-

## Notes
-
```

- Append under `## Activity`:
  ```
  - `<repo>` — <commit message> (<files changed> files)
  ```

### 3. Design decision made
- When the user explicitly chooses between options or makes an architectural call, append to the project note's `## Decisions` section:
  ```
  - <date>: <one-line summary of what was decided and why>
  ```
- If the decision involves a flow, architecture, or component interaction, add a Mermaid diagram right after the bullet:
  ```
  - <date>: <one-line summary>
    ```mermaid
    flowchart TD
      A[Component] --> B[Component]
    ```
  ```
- Use `sequenceDiagram` for API/service flows, `flowchart TD` for architecture/decision trees
- Keep diagrams small (max 6-8 nodes) — they supplement the text, not replace it

### 4. Session end (user says "done", "that's it", "I'm done for today", or similar)
- Append a session summary to today's daily note under `## Notes`:
  ```
  - Session: <1-2 sentence summary of what we accomplished>
  ```
- Update project note **Status** if work is complete (change to `DONE`) or add latest PR links to `## Key PRs`

### 5. Task finish (`done-task.sh` runs)
- Update project note **Status** to `DONE`
- Append final PR links if not already there
- Add a closing summary line under `## Context` if empty

### 6. Staff-track plan awareness (`#staff-track` project notes)
Project notes tagged `#staff-track` (e.g. `projects/Tech Lead Handoff 2H 2026.md`) contain phased plans with `- [ ]` checkboxes and dated **Phase gates**. Treat them as live plans, not static docs.

**Session start** (first interaction of a new conversation), or when the user says "check my plan", "tech lead", "phase gate", "what's next", or similar:
- Read every `#staff-track` note in `projects/`
- Surface: the current phase, count of open items in that phase, and the next upcoming **Gate** date
- If a gate is within 3 working days and open items remain in that phase, call it out

**Item completion**: when a session's work satisfies a plan checkbox (e.g. shipping a PR that maps to a listed item), offer to tick it in the plan note and add a one-line note next to the checkbox (`- [x] Item — 2026-07-15, see [[PR title]]`). Ask before ticking; never auto-tick.

**Fridays** (or when user says "weekly report", "wrap up week", or similar):
- Read the week's daily notes + all `#staff-track` plans
- Offer to (a) audit checkbox progress against the week's Activity entries, (b) draft the pod weekly report via the Claude weekly-report skill, (c) update phase status in the plan note

**Phase gate day**: on a phase's Gate date, run the audit unprompted at session start — list what's checked, what's not, and what would need to slip to the next phase.

### 7. Discovery / study / prep workflow (`new-study.sh` runs)
Studies are read-only investigations that produce an artifact (Confluence one-pager, ADR, agent-file update, spike doc, decision log entry) rather than a code PR. They live at `projects/discovery-<slug>.md` and are indexed at `projects/discovery-index.md`. See also `~/GoProjects/new-study.sh` and `done-study.sh`.

**On `new-study.sh` run**:
- The script creates the discovery note skeleton if it doesn't already exist. Nothing to write from the agent side at study start.
- If the user asks you to "start a study" or "prep a discovery" without running the script, offer to run `new-study.sh <slug> [repo …]` for them instead of hand-crafting the note.

**During the study** — when the user reports a finding, adds a source, or makes an interpretation:
- Append a bullet under `## Findings`, `## Sources`, or `## Open Questions` in the discovery note. Use the safe-append procedure from the section below (read → replace-last-line-plus-append).
- If the user articulates the Question / Artifact / Audience / Time-box out loud (e.g. "the artifact is going to be an ADR"), offer to fill in the corresponding gate field in the note — don't overwrite an existing value without confirmation.

**Artifact drafting**: when the user starts drafting the artifact itself, put v0.1 inline under `## Artifact draft` in the discovery note (or link to it if it's a separate file / Confluence page). This section MUST be non-empty for `done-study.sh` to succeed.

**On `done-study.sh` run**:
- The script updates status to `DONE (YYYY-MM-DD)`, prompts for a harvest target, appends the answer under `## Harvest` in the note, and appends a one-line entry to `projects/discovery-index.md`.
- If the script refuses to close because gate fields are still `TBD`, do NOT suggest `--force` as the first response. Ask the user which gate fields are unanswered and offer to help draft them.

**Session-end summary for studies**: if the current session was a study session, the session-end bullet in the daily note should reference the discovery note by wiki-link, e.g. `Session: read HIPAA safe-harbor rules for tenant onboarding, see [[discovery-hipaa-tenant-scoping]]`.

**Staff-track lens applies**: the tech-lead lens (`tech-lead-lens.instructions.md`) treats discovery notes as strategic artifacts. Apply the audience / iteration-cost / staff-artifact questions to studies the same way as to `#staff-track` project notes. A study with `Audience: TBD` after more than a day is a red flag — call it out.

## How to safely append to a daily or project note

**The failure mode to avoid**: agents guess at the current file contents, call `replace_string_in_file` with a wrong `oldString`, the match fails, and then some agents fall back to `create_file` — which clobbers the whole note. All the user's existing entries disappear.

**The rule**: never `create_file` on a note that already exists. Never guess file contents.

**The procedure for appending**:

1. **Read the file first.** Use `read_file` on the target daily or project note. Do NOT assume contents from an earlier read in the same session — the user may have edited it.
2. **Find the last existing bullet** under the target section (`## Activity`, `## Notes`, `## Decisions`, etc.).
3. **Use `replace_string_in_file`** with:
   - `oldString` = the last existing bullet, exact match (including leading `- `, indentation, and any trailing text)
   - `newString` = that same last bullet + `\n- <your new bullet>`
   This preserves the "after" context automatically because you're replacing what exists, then adding your line below it.
4. **If the section is empty** (just `## Activity\n-\n`), replace the placeholder `-` line with `- <your bullet>`.
5. **If the file does NOT exist**, use `create_file` with the daily-note template from Section 2. This is the only case where `create_file` on a daily note is acceptable.
6. **If `replace_string_in_file` fails**, RE-READ the file. Do NOT retry with the same `oldString` — the mismatch means your assumption is wrong. Do NOT escalate to `create_file` as a fallback.
7. **Multiple bullets to append at once**: use `multi_replace_string_in_file` in a single call, not sequential `replace_string_in_file` calls (each sequential call risks the same mismatch trap).

**For project notes** (`## Decisions`, `## Learnings`, `## Key PRs`): same procedure — read, replace-last-line-plus-append, never rewrite the whole file.

**For ticking a plan checkbox**: read the file, find the exact `- [ ] Item text ...` line, replace with `- [x] Item text ... — YYYY-MM-DD, see [[link]]`. Do NOT rewrite the whole plan.

## Rules

- **Never overwrite** — always append or update specific fields
- **Keep it terse** — bullet points, not paragraphs. Max one line per entry
- **No fluff** — skip entries that add no information ("continued working on X")
- **Don't block the user** — write silently, don't ask permission for vault writes
- **Link related notes** — use `[[Note Name]]` when referencing other project notes
- **Use tags** — add relevant tags (#chathub, #aor, #debugging, #architecture) on the first line after the title
- **Daily notes are append-only** — never modify existing entries in a daily note
- **Create directories if needed** — `daily/` and `projects/` should always exist
- **Use Mermaid diagrams** — when logging decisions or context that involves flows, architecture, or component interactions, include a small Mermaid diagram (`flowchart TD` or `sequenceDiagram`). Keep them tight (max 6-8 nodes). Don't add diagrams for trivial decisions
- **Never use `<...>` for placeholders** — CommonMark treats anything that looks like an HTML tag as one and swallows following content into HTML-block mode, breaking rendering. Use `` `placeholder` `` (inline code), `{placeholder}`, or a plain string like `TBD-date` instead
