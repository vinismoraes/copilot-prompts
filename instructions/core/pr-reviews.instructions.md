---
applyTo: "**"
description: How to handle PR review requests — explain before acting, wait for approval
---

# PR Reviews

When the user asks to review, address, or look at PR feedback:

1. **Always use `gh` CLI** to fetch review comments (`gh api repos/.../pulls/.../comments`)
2. **Explain before acting** — for each comment:
   - Summarize what the reviewer is flagging
   - Explain why it matters
   - Propose one or more fix options
3. **Wait for user approval** before making any code changes
4. Never execute fixes without the user confirming which approach to take
5. **Resolve conversations** after addressing a comment:
   - Reply with "Done." via `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies -f body="Done."`
   - Resolve the thread via GraphQL: `gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: "THREAD_ID"}) { thread { isResolved } } }'`
   - Get thread IDs from `repository.pullRequest.reviewThreads` GraphQL query
6. **Re-request required reviewers** after pushing fixes when your team expects follow-up review:
   - `gh api repos/{owner}/{repo}/pulls/{pr}/requested_reviewers -X POST --input - <<< '{"reviewers":["REVIEWER_OR_BOT"]}'`
   - Confirm reviewer identities with the user before requesting
   - After review is triggered, check for new comments, address them, repeat until no new issues
