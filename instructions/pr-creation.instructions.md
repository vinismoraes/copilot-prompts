---
applyTo: "**"
description: Pull request creation standards — always create as draft, include Jira ticket
---

# PR Creation

## Draft first

- **Always create PRs as draft** using `gh pr create --draft`
- Only mark as ready for review when the user explicitly says so
- To mark ready: `gh pr ready <number>`

## Title format

`[TICKET-123] Short description of change`

- Branch name = Jira ticket number (e.g. `PCHAT-6802`)
- Title uses `[branch]` prefix

## Body format

Follow the repo PR template (`.github/pull_request_template.md`):

```
### JIRA Ticket Reference
https://everlong.atlassian.net/browse/TICKET-123

### Description
What was added/changed and why.

### Potential Impact
Blast radius (BR1–BR5) and mitigation plan if broad.

### Testing
Unit tests, integration tests, manual testing.
```

- Always include the Jira ticket link
- Use `### Description`, not `## Summary`
