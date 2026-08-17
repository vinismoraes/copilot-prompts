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

## Voice: guardrails against AI-ish drift

Grounded in feedback on the Aug 17 Care Finder hard-cut proposal (MS1/7584940056): "writing feels AI-ish, many things not sounding clear or matching our vocabulary." Five specific patterns Victoria flagged inline, and the rules they became.

### The five failure modes

1. **Asserting scope/priority framings the reader hadn't confirmed.**
   - What happened: "Facility comparison is a scope extension" — a categorization I derived from my own read of the bet page. The PM (owner of scope) rejected it as "not correct".
   - Rule: never state scope, priority, or product intent as fact when it came from your own reading of source material. Frame as "my read of X is Y — flag if wrong", or drop the point. The reader owns scope, not you.

2. **Vague phrasing instead of naming the concrete thing.**
   - What happened: "new effort with integration risk we can't estimate until we're in it" — Victoria had to ask "is that the new effort required?" because the actual work (wiring the Book CTA to the Scheduling SDK date/time selector) was never named.
   - Rule: every claim names the concrete thing — the SDK, the CTA, the ticket, the flow, the person. If you catch yourself writing "the effort", "the integration", "the extension", "the intended path", "the headline experience" — stop and name it. If you can't name it, you don't understand it yet and the reader definitely won't.

3. **Internal engineering jargon in stakeholder-facing prose.**
   - What happened: "degraded state", "compare surface", "union-of-rows model" — none appear in the bet page or in shared product vocabulary. PM had to ask what "degraded state" meant.
   - Rule: every term must already appear in the bet page (or equivalent source-of-truth artifact) or be defined inline on first use. When in doubt, use the exact words the bet page uses. If the bet says "comparison view", don't rename it "compare surface".

4. **Aggregated counts instead of concrete lists when the reader wants to click through.**
   - What happened: "≥ 11 tickets" in a deferred bucket, tickets buried in a comma-separated inline list. Victoria: "is it easy to get a list of these tickets?"
   - Rule: when the audience will ask "which ones?", the doc answers without them asking. Options: expand-macro dropdown per bucket, JQL link with the label, or plain bulleted list. Naked counts are anti-user.

5. **Motivational / stakes-framing filler sentences.**
   - What happened: "draw a line", "move the team on", "anchoring the ship on an unknown-shape investigation", "no dead-ends", "the intended long-term path".
   - Rule: cut any sentence that would still make sense with the project name swapped out. Those are AI motivational filler and are the loudest voice tell. Say what happened, what you propose, what you're asking — nothing else.

### Pre-post checklist (must run before publishing to a shared Confluence page)

Answer YES to each. Any NO means revise, or downgrade to a v0.1 stub and get a live read before publishing.

1. **Named things.** Every claim names the concrete artifact (SDK / CTA / ticket / flow / person). Zero "the effort" / "the integration" / "the path".
2. **Vocabulary match.** Every term is in the source-of-truth artifact or defined inline. Zero internal jargon assumed shared.
3. **Scope framings not invented.** Every scope/priority/intent statement is either quoted from a source-of-truth artifact or explicitly framed as "my read — flag if wrong".
4. **Concrete lists, not counts.** Wherever the reader might ask "which ones?", the answer is one click away. No naked "≥ N tickets".
5. **No motivational filler.** Every sentence breaks if you remove the specific detail. Zero "draw a line" / "close out" / "move on" / "headline" / "long-term path" phrases.

### The structural fix: send the shape before you write the page

The Aug 17 doc landed as a polished v1 with confident prose that hid its framing errors — Victoria had to peel them back inline. The voice checklist above catches individual tells; only this catches structural framing errors:

**Before creating the Confluence page**, send the section headers + one-line-per-section summary to the primary reviewer (DM or Slack). Ask "am I framing this the way you'd frame it?" Only publish after they've read the shape. This is the largest single guardrail against the "land fully-formed" anti-pattern.

## Related

- `obsidian-journaling.instructions.md` — how the vault is structured; what each note type contains
- `tech-lead-lens.instructions.md` — when porting strategic docs, the lens's rules about audience and framing also apply
- User memory `confluence-edits.md` — the fetch-before-post rule for shared pages
