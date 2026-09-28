---
description: "Always-on — use the League observability KB articles for any debugging, incident, RCA, latency, or instrumentation work"
---

# Observability KB

League's observability articles live in the knowledge base at `observability/*.md` (source: `EverlongProject/league-ai-knowledge-base/knowledge-base/articles/observability/`). They are bot-maintained, so read them live every time and never keep a local copy that can drift.

## When to load

Load before answering, not after a first guess, when the work involves any of these:

- Debugging a bug report, incident, Rootly page, `#services-errlog` panic, or interrupt-pod ticket
- Latency, error-rate, SLO, or burn-rate questions; "is X slow / failing for tenant Y"
- Writing an RCA or linking metric/log/trace evidence
- Masonry resolver failures or slow nodes
- Adding or changing logs, metrics, spans, or labels in Go code (so the new signal is findable with the documented conventions)
- Checking a change on test envs after a mirrord or `eos deploy` run

## How to load

1. `read_knowledge_base` (League Knowledge Base MCP) with the files that fit the task:
   - `observability/correlation.md`: start here for any investigation (the order to check signals in, and how to jump between them)
   - `observability/logs.md`: Cloud Logging filters, field locations, severity mapping
   - `observability/traces.md`: Cloud Trace filter syntax, span names, Masonry span hierarchy
   - `observability/metrics.md`: PromQL, recording rules, SLI families
   - `observability/labels.md`: which label to filter each protocol by, and how labels map across metrics, logs, and traces
   - `observability/datasources.md`: Grafana URLs, GCP project naming, backend-extension projects
2. If the MCP is down: `gh api repos/EverlongProject/league-ai-knowledge-base/contents/knowledge-base/articles/observability/<file>.md -H "Accept: application/vnd.github.raw"` (needs the sandbox disabled because of the TLS proxy).
3. If an article is wrong or missing something, send it through `send_feedback`. Don't edit the KB by hand.

## Output: queries Vini runs, not queries I run

- Produce ready-to-paste **Logs Explorer filters**, **Cloud Trace filter strings**, **PromQL**, and **Grafana Explore / Cloud Trace deeplinks**, with the placeholders (project, tenant, app, time range) already filled in.
- Never execute `gcloud`, `bq`, `gsutil`, `kubectl`, or Cloud Logging/Trace/Monitoring APIs against League infra, and never generate bulk-export or extraction commands for production data. For data pulls, point to `#team-data-requests`.
- Always give a time range on log/trace queries.
- Log results pasted back may contain PHI or member-level data. If a pasted log entry has health data plus an identifier, stop and follow the PHI rule in the org instructions.
- If `restricted_fields` lists a key but `restricted` has no value for it, that environment strips it on purpose. Say so and point to the approved access process; don't look for the value somewhere else.

## Gotchas to check first (full detail in the articles)

- Each protocol has its own endpoint label: WS `message_type`, REST `route`, Masonry `target`. The wrong one returns no data.
- Use `trace=` in log filters, not `logging.googleapis.com/trace`.
- WS `failure` logs at `WARNING`. Use `severity>=WARNING` for WS failures.
- `application_name` / `service.name` use underscores (`everlong.content_authoring`); k8s labels use hyphens.
- The Masonry root span `owner` is always `domain-masonry`. Filter on `masonry/root_node_owner` instead.
- Use the `backend:*:2m` recording rules instead of raw `rate()` (a GMP staleness workaround).
- The root cause is often in `jsonPayload.restricted.err` or `jsonPayload.message`, not in `payload_error`.
