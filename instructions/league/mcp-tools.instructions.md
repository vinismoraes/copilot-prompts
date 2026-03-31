---
applyTo: "**/mcp/**/*.go"
description: MCP tool development patterns for messaging and connected care
---

# MCP Tool Patterns

## Structure

Follow the established pattern from `messaging/chathub/mcp/ui_tools/`:

```
mcp/
├── mcp_server.go          # MCPServer wrapper, RegisterTools(), Start(), Shutdown()
└── tools/
    └── tool_name/
        ├── tool.go        # BuildTool(), handler()
        └── models.go      # Input/Output types with jsonschema tags
```

## Building a Tool

```go
func BuildTool(deps Dependencies) mcp.Tool[InputType] {
    toolBuilder := mcp.NewToolBuilder[InputType]()
    t, err := toolBuilder.
        WithOwner(logger.YourDomain).
        WithName("tool_name").
        WithDescription("Clear description for LLM routing").
        WithOutputSchema(OutputType{}).
        WithNoAuth().
        WithToolHandlerFunc(func(ctx context.Context, req InputType, result mcp.CallToolResult) *mcp.ToolError {
            return handler(ctx, req, result, deps)
        }).
        Build()
    if err != nil {
        panic(err)
    }
    return t
}
```

## Tool Descriptions

- Write descriptions that help the LLM decide WHEN to call the tool
- Be specific about what data the tool provides and when to use it
- Mention what the tool does NOT do (e.g., "does not return document content")

## Connected Care: Use Extensions Client

- Always use `extensionsClient` methods, never the legacy connector/service layer
- The extensions router handles multi-tenant routing via `ctx.TenantId()`
- Methods: `SearchDocuments()`, `GetDocumentFilters()`, `GetDocumentContent()`

## Privacy

- Metadata tools (search, filters, links): use `WithNoAuth()` — user context from JWT
- Content tools: require explicit consent, log audit events
- Never send raw document bytes to the LLM without consent gating
- Return download URLs instead of content when possible
