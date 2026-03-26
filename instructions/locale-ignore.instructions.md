---
applyTo: "src/el/**/*.go"
description: Go string localization — add locale.Ignore comments to non-user-facing strings
---

# Locale Ignore Comments

This repo runs a `check_strings` linter (`patch_strings -verify`) that flags new string literals as candidates for localization.

Strings that should **not** be localized (log messages, metric names, map keys, internal error messages) must have `// locale.Ignore` on the same line.

```go
// ❌ BAD — linter will fail
logger.New(ctx).Error("Failed to process request", map[string]any{
    "event_id": eventID,
})

// ✅ GOOD
logger.New(ctx).Error("Failed to process request", map[string]any{ // locale.Ignore
    "event_id": eventID, // locale.Ignore
})
```

Common places that need `// locale.Ignore`:
- Logger message strings (`.Error()`, `.Info()`, `.Debug()`, `.Warn()`)
- Map keys in log structured data
- Prometheus metric `Name`, `Help`, and label strings
- Internal `fmt.Errorf()` / error messages not shown to users
- String constants for internal identifiers

If a string **is** user-facing and needs translation, do **not** add the comment — let the linter pick it up so it gets added to the localization pipeline.
