---
applyTo: "**"
description: Rules for porting Obsidian vault markdown notes to Confluence pages. Activates when the user asks to publish, port, or share an Obsidian note on Confluence.
---

# Obsidian → Confluence Porting

Vault path: `~/ObsidianVault/`. Confluence access via the atlassian MCP tools.

## When this applies

Any of:
- User says "port to Confluence", "publish this to Confluence", "share this on Confluence", "make a Confluence page from this note"
- User references an Obsidian note path AND a Confluence destination in the same request
- Follow-up to a note draft with a "when I share it" or "when it goes public" cue

## Before doing anything

Ask (once) if not already specified:
- **Which space** (e.g. MS1, PS1, TEAM). Do not guess.
- **Parent page** (page ID or title). If none, publish as a top-level page in the space.
- **Which sections** to include. Personal working sections are almost never included — see rules below.

Then confirm the full plan (space, parent, title, section list) before creating the page.

## What DOES NOT port

Strip these from the Obsidian source before creating the Confluence page:
- **`## Decisions` sections** — personal working log, not audience content
- **`## Learnings` sections** — same
- **`## Open Questions` addressed only to yourself** — include only if the doc is a socialization stub asking the audience to answer them
- **Anything with `#staff-track` / personal tags** — those are Obsidian vault taxonomy, meaningless on Confluence
- **`[[wiki links]]`** — Obsidian-only. Either (a) remove entirely if the reference isn't useful outside the vault, or (b) rewrite as plain text ("see the Tech Lead handoff plan") or as a Confluence link if the referenced doc also lives on Confluence
- **Frontmatter block** (`---` YAML) — Confluence uses page properties, not frontmatter
- **File-metadata lines** like `**Status**: DRAFT`, `**Author**: Vini` — Confluence tracks these natively

## What DOES port cleanly

- External URLs (Confluence, GitHub, etc.) — 1:1
- Standard markdown headings, bold, italic, inline code, code blocks
- Tables — column widths may reset under the new Confluence editor; acceptable
- Task checkboxes `- [ ]` / `- [x]` — render as Confluence tasks (interactive)
- Mermaid diagrams — supported via the Mermaid macro; verify after publish

## Publishing procedure

1. Read the Obsidian source file with `read_file`.
2. Apply the strip rules above; show the resulting content to the user for a last look.
3. Wait for approval. Do not publish silently.
4. Use `mcp_atlassian_mcp_confluence_create_page` (or the equivalent create tool). Prefer `content_format=markdown` unless the doc has structured tables with layout requirements, in which case use `storage` (XHTML).
5. After publish, share the page URL with the user in the reply.

## After publishing — updates

If the user later asks to update a shared Confluence page, follow the `confluence-edits.md` user memory rule: **re-fetch the page immediately before posting**, apply your edit to the just-fetched content, and post within seconds. There is no version-guarded patch — you're doing a full-content REPLACE. Any gap between fetch and post risks clobbering teammate edits.

## Common porting mistake to avoid

Do NOT port working documents (project notes, plans, session logs) in full. They contain personal reasoning that should stay in the vault. When in doubt, ask the user which sections to include — assume less rather than more.

## Filter test before posting to shared pages

Before writing a bullet to any shared page (Confluence daily updates, weekly reports, stakeholder docs, pod pages), each entry must pass ALL three:

1. **Public deliverable** — links to a PR, ticket, published doc, or team-visible artifact.
2. **Team-legible** — someone else on the pod can act on or verify it.
3. **No personal paths / tooling** — doesn't reference `~/.claude/`, `~/.copilot/`, `~/ObsidianVault/`, `copilot-prompts`, personal MCP config, memory files, or agent-instruction changes. Meta-work about *how you work* is not shipped work-product.

If any fails: it stays in the Obsidian vault only. When in doubt, drop the bullet and ask.

## Related

- `obsidian-journaling.instructions.md` — how the vault is structured; what each note type contains
- `tech-lead-lens.instructions.md` — when porting strategic docs, the lens's rules about audience and framing also apply
- User memory `confluence-edits.md` — the fetch-before-post rule for shared pages
