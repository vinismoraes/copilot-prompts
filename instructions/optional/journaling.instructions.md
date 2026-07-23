---
applyTo: "**"
description: Persist engineering activity to a local journal so the agent has context across sessions
---

# Engineering Journaling

Extends agent memory across sessions by writing to a local, tool-agnostic markdown journal. The vault is human-readable so it doubles as a personal engineering log.

## Configuration

Set `JOURNAL_ROOT` in your environment to point at your journal directory. Common choices:

- Obsidian: `~/ObsidianVault/`
- Plain markdown notes: `~/notes/`
- Any other markdown folder you already use

**If `JOURNAL_ROOT` is unset OR the directory does not exist, this file has no effect.** Skip journaling silently — do not create the directory automatically and do not mention it to the user.

Two subdirectories are used:

- `${JOURNAL_ROOT}/projects/` — one long-lived note per ticket/task
- `${JOURNAL_ROOT}/daily/` — one note per day

Create them on first use if `JOURNAL_ROOT` exists but the subdirs don't.

## When to write

### 1. Task start (new branch, new ticket)

Check if `projects/${TICKET}.md` exists. If not, create it with this skeleton:

```markdown
# ${TICKET} ${Short Description}

**Ticket**: ${ticket-tracker-url}
**Branch**: ${branch-name}
**Status**: IN PROGRESS
**Repos**:

## Context

## Key PRs

## Decisions
```

If it exists, update **Status** to `IN PROGRESS` and update **Branch** if it changed. Never overwrite existing sections.

### 2. Commit proposed (before asking the user for commit confirmation)

Append a one-line bullet under `## Activity` in today's daily note at `daily/${YYYY-MM-DD}.md`. Format:

```
- `${repo}` — ${commit message} (${files changed} files)
```

Create the daily note from this skeleton if it doesn't exist:

```markdown
# ${YYYY-MM-DD}

## Activity
-

## Notes
-
```

### 3. Design decision made

When the user explicitly picks between options or makes an architectural call, append to the project note's `## Decisions` section:

```
- ${date}: ${one-line summary of what was decided and why}
```

### 4. Session end ("done", "that's it", "I'm done for today", or similar)

Append a session summary under `## Notes` in today's daily note:

```
- Session: ${1-2 sentence summary of what was accomplished}
```

If the task is complete, also update the project note's **Status** to `DONE`.

## Rules

- **Never overwrite.** Read the file, find the last existing bullet under the target section, then `replace_string_in_file` with `oldString` = that last bullet and `newString` = that bullet + `\n- ${new bullet}`.
- **If `replace_string_in_file` fails, re-read the file.** Do not retry with the same `oldString`. Do not fall back to `create_file` on a note that already exists — that clobbers the user's own edits.
- **Never use `create_file` on an existing note.** The only case where `create_file` on a daily or project note is acceptable is when the file genuinely does not exist yet.
- **Keep entries terse.** One line per bullet. Skip entries that add no information ("continued working on X").
- **Never use `<...>` for placeholders.** CommonMark treats HTML-looking tags as HTML blocks and can break rendering downstream. Use `` `placeholder` `` or `${placeholder}` instead.
- **Do not block the user.** Write silently as a side effect; do not ask permission for journal writes.
