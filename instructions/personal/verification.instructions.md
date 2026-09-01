---
description: How to establish a fact before writing it down. Covers query caps, artifact existence vs adoption, and absence-as-evidence. Sibling to plain-language.instructions.md — that one governs how it reads, this one governs whether it is true.
---

# Verification

Scope: any factual claim written into a document, ticket, message, or report —
counts, dates, status, ownership, adoption, whether something happened.

`plain-language.instructions.md` governs whether a sentence is *readable*. This
one governs whether it is *true*. A claim can pass that checklist perfectly and
still be wrong, and a confidently-worded wrong claim is worse than a vague one.

The rule underneath all three below: **tools return artifacts, not facts.**
Jira, Confluence, Slack and GitHub can show you that a page exists or a row is
missing. They cannot tell you what anyone intended.

## 1. A result that equals the limit is a cap, not a count

Never report a number straight off a query without checking whether the query
truncated it.

```
❌ jira_search(..., limit: 50) → 50 rows → "50 tickets closed"
✅ 50 rows returned with limit 50 → the query capped. Paginate via
   next_page_token, or slice the date range, until no page comes back full.
   Then sum. → "171 tickets closed"
```

Tells that you are looking at a cap, not a total:

- Row count exactly equals the limit you passed.
- The response carries a `next_page_token`, `cursor`, or `has_more`.
- `total` is `-1`, `null`, or absent — several APIs (Jira's included) do not
  return a real total and will happily hand you a full page with no warning.

`gh search` has its own ceiling; `--limit` above the returned count is the only
proof it did not truncate. Same for Confluence search and Slack search.

Two more traps in the same family:

- **Status filters silently exclude.** `status = Done` matches one named status;
  `statusCategory = Done` matches every status in the done column. Prefer the
  category unless you mean the specific status.
- **Derived breakdowns inherit the truncation.** If the total was capped, every
  "X of which were under epic Y" split computed from those rows is wrong too.
  Recompute from a complete set or drop the breakdown.

When an exact count is expensive to establish, publish the live query link and
let the reader see the current number, rather than freezing a guess.

## 2. Existence is not publication, and publication is not adoption

Finding a document proves someone created a document. Nothing more.

```
❌ Four template pages exist in the space → "X published templates; they are
   the org standard now"
✅ Four template pages exist, created by X between Aug 26–31. No announcement
   found in Slack. Two pods are using them; both are X's own pods.
```

Three separate claims, each needing its own evidence:

| Claim | What actually proves it |
| --- | --- |
| It exists | The page/ticket/PR itself |
| It was announced | A message, email, or meeting note announcing it |
| It was adopted | Usage by people other than the author |

If you can only evidence the first, write only the first — and say plainly that
you looked for the others and did not find them. "I could not find an
announcement" is a useful sentence. Inventing "published" is not.

## 3. A missing artifact is a question, not a finding

Absence has many causes and only one of them is "it stopped".

```
❌ Only one weekly thread where three were expected → "Lapsed. Ran one week
   only."
✅ "I only found one thread covering those three weeks — did it stop, or was
   there nothing to re-post?" → the goal did not change across a two-week
   bet, so one thread covered it. Nothing had lapsed.
```

Before writing that something stopped, slipped, or was skipped, ask the person
who owns it. This matters most when the subject is **someone else's work** and
the audience is **their manager or peer** — exactly the case where a wrong
inference does real damage and the cost of one question is nil.

A verified gap is fine to state. The weekly-report gap in the same document was
verified: absent for three named weeks, and cross-checked against a sibling pod
that shipped all three. That is evidence, not inference.

## Checklist

Before any factual claim goes into something another person reads:

1. **Every number came from a query proven not to have truncated.**
2. **No "published" / "adopted" / "standard" without evidence beyond the artifact existing.**
3. **No "stopped" / "lapsed" / "dropped" about someone else's work without asking them.**
4. **Status, ownership and dates re-read from the source today**, not recalled
   from earlier in the session.
5. **Where the number will drift, link the live query** instead of freezing it.

## Why this exists

**2026-09-01**, drafting the sabbatical-return handoff. Four separate claims
were wrong, and the user caught all four:

- "50 MSP3 tickets closed" — the query had `limit: 50` and returned exactly 50.
  Real number: 171. The epic breakdown derived from those rows was wrong too.
- "David published MS1 templates … the org standard" — pages existed, no
  announcement anywhere in Slack.
- "Weekly pinned thread — Lapsed" — one thread deliberately covered a two-week
  bet whose goal did not change.
- "demoed at LEAP on Aug 31" — the conference demo was cancelled.

Every one was an inference from an artifact, stated as fact, in a document
about a colleague's own work written for their manager to read.

## Related

- `plain-language.instructions.md` — the sibling rule: how the claim reads once
  it is true.
- `obsidian-to-confluence.instructions.md` § Voice — rule 3 there ("scope
  framings not invented") is the same failure applied to product scope.
