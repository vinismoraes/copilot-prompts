---
applyTo: "**"
description: Pull request creation standards — always create as draft, include issue tracker link when available
---

# PR Creation

## Draft first

- **Always create PRs as draft** using `gh pr create --draft`
- Only mark as ready for review when the user explicitly says so
- To mark ready: `gh pr ready <number>`

## Title format

`[TICKET-123] Short description of change`

- If the branch name includes an issue key, use `[branch]` prefix in the title
- Title uses `[branch]` prefix

## Body format

Follow the repo PR template (`.github/pull_request_template.md`):

```
### Issue Tracker Reference
https://tracker.example.com/browse/TICKET-123

### Description
What was added/changed and why.

### Potential Impact
Blast radius (BR1–BR5) and mitigation plan if broad.

### Testing
Unit tests, integration tests, manual testing.
```

- Include the issue tracker link when a ticket exists
- Use `### Description`, not `## Summary`
