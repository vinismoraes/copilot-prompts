---
applyTo: "**/*.go"
description: Go coding standards and PR conventions for all Go files
---

# Go Standards

## Formatting

- Always run `gofmt -w` on modified `.go` files before committing
- Watch for map literal alignment — all values must align to the longest key

```go
// ❌ BAD
map[string]any{
    "operation": "get_session",
    "error":     err,
    "error_type": fmt.Sprintf("%T", err),
}

// ✅ GOOD
map[string]any{
    "operation":  "get_session",
    "error":      err,
    "error_type": fmt.Sprintf("%T", err),
}
```

## Localization (locale.Ignore)

- The `check_strings` linter detects string literals that look like user-facing text and flags them for translation
- Logger messages, internal constants, and non-user-facing strings must have a `// locale.Ignore` comment on the same line to suppress the linter
- This applies to string values in logger `map[string]any{}` payloads, internal error messages, and metric/config names
- Check existing patterns in the same file for guidance — if sibling strings have `// locale.Ignore`, new strings in the same context need it too

```go
// ❌ BAD — linter will flag "5s" as a missing translation string
logger.New(ctx).Warning("timeout detected", map[string]any{
    "timeout": "5s",
})

// ✅ GOOD
logger.New(ctx).Warning("timeout detected", map[string]any{
    "timeout": "5s", // locale.Ignore
})
```

## Testing

- Write unit tests as **table-driven tests** with a single test method per function
- Use `t.Run(name, func(t *testing.T) { ... })` for each test case
- Name test cases descriptively: what's being tested and the expected outcome

```go
// ✅ GOOD
func TestGetDocumentFilters(t *testing.T) {
    tests := []struct {
        name    string
        setup   func()
        want    *Filters
        wantErr bool
    }{
        {"returns filters for valid tenant", ...},
        {"returns error when extension unavailable", ...},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) { ... })
    }
}

// ❌ BAD: multiple test functions for one function, no table
func TestGetDocumentFiltersSuccess(t *testing.T) { ... }
func TestGetDocumentFiltersError(t *testing.T) { ... }
```

## Mocking

- Use **code-generated mock interfaces** (mockery, mockgen, or project conventions)
- Never hand-write mock structs — generate them from interfaces
- Place mocks in a `mocks/` subdirectory or `*_gen.go` files

## Comments

- Keep comments **concise** — one line when possible
- Only comment **non-obvious intent, trade-offs, or constraints**
- Never narrate what code does ("increment counter", "return result")
- Never use comments to explain changes being made

```go
// ❌ BAD
// Get the document filters
filters, err := client.GetDocumentFilters(ctx, params)

// ✅ GOOD (explains WHY, not WHAT)
// Extensions client handles tenant routing internally via ctx.TenantId()
filters, err := client.GetDocumentFilters(ctx, params)
```

## Security

- Never expose raw document content to external systems without consent gating
- Validate all inputs from MCP tool requests before passing to service layer
- Use `ctx.UserId()` and `ctx.TenantId()` from JWT — never trust client-provided IDs
- Log security-relevant events (consent, document access) with structured fields

## Documentation

- Write documentation **after** implementation is complete, not before
- Do not create or update README/docs during development — do it as a final step
- This avoids constant doc updates during iterative changes
