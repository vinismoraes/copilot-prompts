---
applyTo: "**"
description: PR comment tone and workflow — positive, concise, always confirm before posting
---

# PR Comments

## Workflow

1. **Draft the comment** and show it to the user first
2. **Wait for approval** before posting — never post without confirmation
3. Always post inline on the relevant line/thread, not as a standalone review

## Tone

- Be **positive** — start by acknowledging the author's effort or good ideas
- Use **simple, concise language** — no corporate-speak or over-explanation
- Keep it short — say what needs to change and why, skip the preamble
- Frame suggestions as improvements, not criticisms
- When disagreeing with a decision, explain the reasoning without being dismissive

```
✅ GOOD
"Nice approach for the dispatch logic! One concern: the type assertion
here can silently fail — safer to put the allowlist on the wrapper directly."

❌ BAD
"This code is fragile. The type assertion is a problem. You should
refactor this to pass the allowlist through the wrapper struct."
```

## When suggesting changes

- Acknowledge what the author got right before pointing out issues
- Give a concrete suggestion or code snippet
- If the suggestion is optional / a nit, say so explicitly
