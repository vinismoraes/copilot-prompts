---
applyTo: "**"
description: Git commit message conventions
---

# Git Commits

- Commit messages must be **one line**, under 72 characters
- No multi-line body or extended description
- Focus on WHAT changed, not WHY or HOW
- Use lowercase, imperative mood ("fix", "add", "update", not "fixed", "added")

```
✅ GOOD
fix privacy language conflict in plan
add search_health_documents MCP tool
update extensions client mock for tests

❌ BAD
Add tool design principles for performance and resilience

Captures lessons on fat-vs-thin tools, structured error messages,
chain depth minimization, and latency budgets to guide implementation.
```
