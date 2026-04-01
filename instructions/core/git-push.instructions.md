---
applyTo: "**"
description: Git commit and push workflow — always ask for confirmation before committing or pushing
---

# Git Commit and Push

**Always ask for confirmation before any commit or push**, including when addressing PR review comments.

1. **Always create a new commit** — never amend pushed commits
2. **Show the proposed changes** (files, commit message) and wait for user approval
3. When confirmed, commit and push together with `git push -u origin HEAD`
4. **Review PR description after each push** — if the scope of changes has evolved beyond what the current PR description covers (e.g. new features, removed fields, architectural changes), suggest a description update before moving on

```
✅ GOOD
"Here are the changes — ready to commit and push?"
(user confirms)
git add <files> && git commit -m "message" && git push -u origin HEAD

❌ BAD
git commit --amend (on already-pushed commits)
git commit && push without asking first
git commit && push immediately after addressing PR review comments
```
