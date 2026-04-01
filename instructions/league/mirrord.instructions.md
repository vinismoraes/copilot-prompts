---
applyTo: "**"
description: Running services locally with mirrord for remote testing
---

# Mirrord

Use mirrord to run a service locally while connected to a remote test environment's Kubernetes cluster.

## Prerequisites

- `gcloud`, `kubectl`, and `mirrord` must be installed
- Authenticated with gcloud (`gcloud auth login`)
- mirrord operator license (auto-upgrades via brew daily)

## Running a service

```bash
cd ~/GoProjects/services/src/el
MIRRORD_ROUTE=<your-value> ./run_with_mirrord.sh <app-name> <environment>
```

### Arguments

- `<app-name>`: Name of the app under `src/el/apps/` (e.g. `messaging`, `api`, `benefits`)
- `<environment>`: GCP environment (e.g. `test2-ca`, `test4-ca`). The `league-` prefix is added automatically

### MIRRORD_ROUTE

- Set `MIRRORD_ROUTE` to a unique personal value (e.g. your name) to only route traffic with `X-League-Mirrord-Route=<your-value>` to your local process
- This allows multiple people to use the same environment concurrently
- Set `MIRRORD_ROUTE=` (empty) to route ALL traffic to your local process — coordinate in `#project-ai-testing-envs` first

### Examples

```bash
# Route only labeled traffic to your local messaging app in test2-ca
MIRRORD_ROUTE=vmoraes ./run_with_mirrord.sh messaging test2-ca

# Route ALL traffic (exclusive use of the environment)
MIRRORD_ROUTE= ./run_with_mirrord.sh messaging test2-ca
```

## What the script does

1. Validates the app directory exists and environment name is valid
2. Switches kubectl context to the target GCP project and namespace
3. Checks if someone else is already using mirrord for the same app (when `MIRRORD_ROUTE` is unset)
4. Builds the app with `go build -tags=cse,mirrord`
5. Runs via `mirrord exec` targeting the deployment in the remote cluster

## Available apps

Any directory under `src/el/apps/` — common ones: `messaging`, `api`, `benefits`, `claims`, `care_finder`, `connected_care`, `content_authoring`, `dynamic_questionnaire`

## Common environments

- `test2-ca` — Canadian test environment
- `test4-ca` — Canadian test environment
- Other test envs follow the pattern `test<N>-ca` or `test<N>-au`

---

## AOR / GC (agent-orchestrator repo)

For the `agent-orchestrator` and `guarded-conversation` Python services, use the `make mirrord` target from the `agent-orchestrator` repo root.

### Running

```bash
cd ~/GoProjects/agent-orchestrator
MIRRORD_ROUTE="<your-name>" PRETTY_LOGS=1 make mirrord <aor|gc> <testX>
```

- `PRETTY_LOGS=1` pipes output through a log formatter for readability
- `<aor|gc>`: target app (`aor` or `agent-orchestrator`, `gc` or `guarded-conversation`)
- `<testX>`: environment (e.g. `test2`, `test4`, `test2-ca`, `league-test2-ca`)

### Testing with SDK Presenter (web app, league tenant)

When `make mirrord` starts, a **sticky header bar** appears at the top of the terminal with a link to the SDK Presenter web app. The environment and mirrord route are pre-populated in the URL.

- URL format: `https://sdk-presenter.league.dev/?env=test2-ca&mirrord=<your-route>`
- The URL is **shareable** — send it to others so they can interact with your local WIP changes
- Log in with: `jjadmin@league.com` / `12345678`
- Click the live chat button at the bottom right to interact with your local changes
- Limitation: only works on the web app and for the `league` tenant

### Testing with CLI chat

```bash
# Terminal 1: Start mirrord
MIRRORD_ROUTE="your-name" PRETTY_LOGS=1 make mirrord aor test2

# Terminal 2: Port-forward
mirrord port-forward -L 18080:agent-orchestrator:8080 -n test2

# Terminal 3: CLI chat
AOR_BASE_URL='localhost:18080' MIRRORD_ROUTE='your-name' make up-chat
```

- At auth prompts, press Enter to use defaults (generates a local mock token)
- CLI chat hits AOR directly and does not test the full upstream stack (SDK, auth, messaging)

### Steal-all mode

If `MIRRORD_ROUTE` is empty or unset, mirrord runs in steal-all mode, intercepting **all** traffic. This blocks others. Coordinate in `#project-ai-testing-envs` first.

### Useful commands

- `mirrord operator status` — see who's currently running mirrord on the target cluster (requires kubectl context set to the target environment)

### Config overrides

mirrord uses remote app configs by default. To override locally:

```bash
cp apps/agent-orchestrator/src/config-override.example.toml apps/agent-orchestrator/src/config-override.toml
cp apps/guarded-conversation/src/config-override.example.toml apps/guarded-conversation/src/config-override.toml
```

Agent YAML files (e.g. `root.yaml`) are always read from local filesystem — changes reflect automatically.

### Troubleshooting

- When restarting the local app, **end the chat and start a new one** (or new session if using CLI)
- mirrord does not replace deploying to testX — do a final smoke-check via Cloud Deploy before merging
- **Always terminate the current mirrord terminal before starting a new build or session** — abandoned terminals leave stale sessions that lock the route. Stale sessions cannot be deleted (RBAC `container.thirdPartyObjects.delete` permission missing) and take ~20 minutes to expire. Never work around stale sessions by switching to a different route — that just compounds the problem.
