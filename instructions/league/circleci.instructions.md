---
applyTo: "**"
description: CircleCI CI/CD interaction via API
---

# CircleCI

Use the CircleCI API with `$CIRCLE_TOKEN` (set in shell env) to inspect and manage CI.

## Checking CI Status

1. Get pipelines for a branch:
```
curl -s -H "Circle-Token: $CIRCLE_TOKEN" \
  "https://circleci.com/api/v2/project/gh/<owner>/<repo>/pipeline?branch=BRANCH"
```

2. Get workflows for a pipeline:
```
curl -s -H "Circle-Token: $CIRCLE_TOKEN" \
  "https://circleci.com/api/v2/pipeline/PIPELINE_ID/workflow"
```

3. Get jobs for a workflow:
```
curl -s -H "Circle-Token: $CIRCLE_TOKEN" \
  "https://circleci.com/api/v2/workflow/WORKFLOW_ID/job"
```

4. Get job step details (v1.1 API, basic auth):
```
curl -s -u "$CIRCLE_TOKEN:" \
  "https://circleci.com/api/v1.1/project/github/<owner>/<repo>/JOB_NUMBER"
```

5. Fetch step output logs via `output_url` from step actions.

## Re-running Failed Jobs

```
curl -s -X POST -H "Circle-Token: $CIRCLE_TOKEN" -H "Content-Type: application/json" \
  "https://circleci.com/api/v2/workflow/WORKFLOW_ID/rerun" \
  -d '{"from_failed": true}'
```

## Workflow

- Always check CI after PR creation or new pushes
- When `unit_tests` fails, fetch logs to determine if failure is related to our changes
- If unrelated (flaky test in another package), rerun from failed
- If related, fix the issue before requesting review
