---
applyTo: "**"
description: League Health Technology security guardrails — HIPAA platform
---

# League Security Policy

This codebase is part of a HIPAA-governed health technology platform.

NEVER run or suggest: gcloud, bq, gsutil, kubectl, helm, mongosh, psql, mysql, snowsql, ssh, nc, socat, openssl s_client, sudo, or any command that accesses *.googleapis.com, *.mongodb.net, or database connection strings.

NEVER read, print, or operate on: .env, *.pem, *.key, serviceAccountKey*, *credentials*.json, ~/.config/gcloud/, ~/.ssh/, ~/.aws/.

Do not include PHI in examples. Use placeholder IDs (patient-uuid-xxxx).

Never hardcode API keys or tokens. Use process.env references only.
