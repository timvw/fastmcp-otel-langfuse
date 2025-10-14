# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-14

### Changed
- **BREAKING**: Switched from HTTP headers to `_meta` field for trace context propagation
- Updated `otel_utils.py` to use `_meta` field convention instead of HTTP headers
- Modified server tools to accept `_meta` parameter
- Updated client to inject context into `_meta` field instead of HTTP headers
- Replaced `with_otel_context_from_headers` decorator with `with_otel_context_from_meta`

### Added
- `inject_otel_context_to_meta()` utility function for client-side context injection
- `extract_otel_context_from_meta()` utility function for server-side context extraction
- Comprehensive documentation on `_meta` approach in README
- Examples showing JSON-RPC request structure with `_meta` field
- Comparison table: HTTP headers vs `_meta` field approaches
- References section with links to MCP spec, OpenTelemetry, and W3C standards

### Benefits
- **Transport Agnostic**: Now works with stdio, HTTP, and SSE transports
- **Standards Based**: Follows emerging MCP standard for metadata propagation ([PR #414](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/414))
- **Interoperable**: Compatible with `openinference-instrumentation-mcp` and other MCP tracing tools
- **W3C Compatible**: Maintains same W3C Trace Context format (traceparent, tracestate, baggage)

### Migration Guide

#### Before (HTTP headers approach):

**Server:**
```python
@mcp.tool()
@otel_utils.with_otel_context_from_headers
@observe
async def get_weather(location: str) -> dict:
    pass
```

**Client:**
```python
carrier = {}
inject(carrier)
transport = StreamableHttpTransport(url="...", headers=carrier)
await client.call_tool("get_weather", {"location": "NYC"})
```

#### After (_meta field approach):

**Server:**
```python
@mcp.tool()
@otel_utils.with_otel_context_from_meta
@observe
async def get_weather(location: str, _meta: dict | None = None) -> dict:
    pass
```

**Client:**
```python
from weather_assistant.utils.otel_utils import inject_otel_context_to_meta

meta = inject_otel_context_to_meta()
await client.call_tool("get_weather", {
    "location": "NYC",
    "_meta": meta
})
```

## [1.0.0] - 2025-09-27

### Added
- Initial implementation with HTTP header-based trace context propagation
- FastMCP server with OpenTelemetry and Langfuse integration
- Streamlit client for weather assistant
- Example weather and forecast tools
- Docker compose setup for local development
