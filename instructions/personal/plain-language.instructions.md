---
description: Plain-language rules for anything written for another human — Confluence, Slack, Jira, PR descriptions, weekly reports, handoff docs. Expand internal labels, explain referenced documents, gloss coined phrases.
---

# Plain Language

Scope: everything written for another human — Confluence pages, Slack posts, Jira
comments and descriptions, PR descriptions, weekly reports, handoff docs, kickoff
recaps, retro summaries. Not code comments, not commit messages.

The test for every sentence: **could someone who has been away for a month act on
this without asking a follow-up question?** If not, the sentence is not finished.

## 1. Private coordinates must be expanded on first use

These are labels that mean something to the people who were in the room and
nothing to anyone else. They are the single biggest source of unreadable
internal writing.

Never ship one bare:

- **Gate labels** — "Gate A", "Gate B", "Gate C". These name a validation step
  nobody outside the ticket can decode. Write what the gate *is*.
- **Phase / wave labels** — "Phase 0", "Day 1", "next wave", "Enh 2", "Enhancement 3".
- **Decision codes** — "D1", "D3", "option C", "A1", "J4".
- **Week numbers** — "W33", "Week 34". A returning reader has to count.
- **Internal shorthand for a decision** — "the hard cut", "the rename", "the
  reframe", "the pivot".

```
❌ Gate B validation on test2-ca passed for both resolvers.
✅ Both resolvers were validated end-to-end on test2-ca — the last check before
   the tickets close.

❌ Nothing for W33, W34 or W35.
✅ Nothing for the weeks of Aug 10, Aug 17 or Aug 24.

❌ Per D3, notApplicable stays internal.
✅ We decided (Aug 20) that the "not applicable" marker stays internal to row
   filtering — it is never sent to clients.
```

If the label is genuinely useful as a handle the team reuses, define it once in
the doc and then use it. Define-then-use is fine. Use-without-defining is not.

## 2. A referenced document must carry what it contains

Naming a doc, page ID, ticket, or PR is not a reference — it is homework
assigned to the reader. Every pointer says what is inside and why they would
open it.

```
❌ See the bet page. See MS1/7584940056. Context is in the arch doc.
❌ Care Finder Comparison — hard cut and leftovers (MS1/7584940056)

✅ The record of the Aug 14 scope cut — what shipped, what was deferred, and
   where those tickets went.
✅ Architecture & Context — start here; the decision log is at the bottom.
```

Same for tickets: `MSP3-260` alone is a lookup. `MSP3-260 (renaming the Go
internals to be entity-generic)` is a reference.

An index or link list is not exempt. That is where this rule matters most,
because a bare list of page titles is the most common form of it.

## 3. Coined expressions get glossed inline, every time

If you or the pod invented the phrase, the reader did not. Gloss it on first
use in *each* document — not once ever, not "they'll remember from last time".

Real examples that needed glossing and did not have it:

- "degraded state" → the comparison returned fewer entities than the user picked
- "compare surface" → the comparison screen
- "signal thread" → one pinned Slack thread a week for blockers and decisions
- "union-of-rows model" → the table shows every row any selected entity has data for
- "agp profile" → one command that loads the pod's skills into Claude, Gemini and Codex

## 4. Name the thing, not the category

Covered at length in `obsidian-to-confluence.instructions.md` § Voice, and it
belongs here too because it is the same failure: "the effort", "the
integration", "the intended path", "the headline experience". Name the SDK, the
CTA, the ticket, the flow, the person. If you cannot name it, you do not
understand it yet.

## 5. Acronyms and product names get four words of expansion

First use only, and only when the audience might not have it. "LEAP" is a sales
conference. "AORTA", "CACT", "EOS", "Forge Console", "PAIR" — check whether the
reader has this before assuming. Cost of expanding when unnecessary is four
words; cost of not expanding is a message back.

Do not expand terms the audience demonstrably shares — that reads as talking
down. A backend EM does not need "fails open" defined; a PM might.

## Checklist before posting

Run this on anything going to a person who was not in the room:

1. **No bare gate / phase / decision codes.** Every one is expanded or replaced.
2. **No bare week numbers.** Dates instead, or dates alongside.
3. **Every doc, page, ticket and PR reference says what is in it.**
4. **Every coined phrase is glossed inline** — in this document, not a previous one.
5. **Nothing is called "the effort" / "the integration" / "the change".**
6. **Read it as someone back from four weeks off.** Any sentence that produces a
   question instead of an action gets rewritten.

## Why this exists

Two separate rounds of real feedback:

- **2026-08-17**, Victoria on the Care Finder hard-cut proposal (MS1/7584940056):
  "writing feels AI-ish, many things not sounding clear or matching our
  vocabulary." Five inline corrections, all traceable to unexplained internal
  framing. Full breakdown in `obsidian-to-confluence.instructions.md` § Voice.
- **2026-09-01**, drafting the sabbatical-return handoff for Vincent. First
  draft referenced pages by space/ID with no description, used "LEAP", "hard
  cut" and "signal thread" undefined, and gave gaps as "W33, W34, W35" to a
  reader who had been out seven weeks. Every one of those was caught in review,
  not in drafting.

The pattern in both: the writing was accurate and unreadable at the same time.
Accuracy is not the bar.

## Related

- `obsidian-to-confluence.instructions.md` § Voice — the five AI-drift failure
  modes and the pre-post checklist for shared Confluence pages. Overlaps on
  "name the thing"; that file is porting-specific, this one applies everywhere.
- `tech-lead-lens.instructions.md` — skimmability and audience tests for
  strategic docs.
