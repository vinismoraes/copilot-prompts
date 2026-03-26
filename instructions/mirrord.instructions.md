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
- Set `MIRRORD_ROUTE=` (empty) to route ALL traffic to your local process — coordinate in `#project-stage-testing` first

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
