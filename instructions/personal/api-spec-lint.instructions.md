---
applyTo: "**/api-specs/**/*.yaml"
description: Run spectral lint on API spec files before committing
---

# API Spec Linting (Spectral)

Before committing changes to API spec YAML files in the `services` repo, **always run spectral locally**:

```bash
cd $SERVICES_REPO && npx @stoplight/spectral-cli lint <spec-file> --ruleset api-specs/.spectral-ci-json-api.yaml
```

This runs the same JSON:API ruleset as the `spectral-lint` CI job.

## Workflow

1. After editing any file under `api-specs/`, run spectral on the changed file
2. If any errors are reported, **fix them before committing**
3. Only propose the commit once spectral passes with no errors

## Common rules

- **api-content-type**: Only allowed content types: `application/vnd.api+json`, `application/fhir+json`, `image/*`, `multipart/form-data`, `application/octet-stream`, `application/vnd.apple.pkpass`
- **jsonapi-post-patch-response-code**: POST endpoints must return `201`, not `200`
- **oas3-unused-component**: No unused schema definitions — remove or reference them

## Spelling

The `check-spelling` CI job uses an allow-list at `.github/actions/spelling/expect.txt`. If a new domain term (e.g. `chathub`) is flagged, add it alphabetically to that file.
