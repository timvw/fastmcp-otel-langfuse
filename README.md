# FastMCP with OpenTelemetry and Langfuse

A complete example demonstrating distributed tracing in FastMCP applications using OpenTelemetry context propagation and Langfuse for LLM observability.

📝 **Blog Post**: [Distributed Tracing with FastMCP: Combining OpenTelemetry and Langfuse](https://timvw.be/2025/06/27/distributed-tracing-fastmcp-langfuse-opentelemetry/)

## Overview

This repository shows how to:
- Build MCP servers with proper distributed tracing
- Propagate OpenTelemetry context via MCP `_meta` field (transport-agnostic)
- Integrate Langfuse for LLM-specific observability
- Maintain trace hierarchy across client-server boundaries

## Features

- 🔍 **Distributed Tracing**: Seamless trace context propagation between MCP client and server
- 🚀 **Transport Agnostic**: Works with stdio, HTTP, and SSE transports via `_meta` field
- 📊 **LLM Observability**: Track token usage, costs, and latencies with Langfuse
- 🎯 **Clean Architecture**: Decorator-based approach for minimal code intrusion
- 🐳 **Docker Ready**: Includes docker-compose setup for local development
- 🔗 **Standards Based**: Uses W3C Trace Context format and MCP protocol conventions

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/timvw/fastmcp-otel-langfuse.git
cd fastmcp-otel-langfuse
```

### 2. Set Up Langfuse

Follow the [official Langfuse Docker Compose guide](https://langfuse.com/docs/deployment/local):
```bash
# In a separate directory
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker-compose up -d
```

Then create a project and get your API keys from http://localhost:3000

### 3. Configure Environment

Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your Langfuse API keys
```

### 4. Install Dependencies

```bash
uv sync
```

### 5. Run the Example

```bash
# Terminal 1: Start the server
uv run python -m weather_assistant.server

# Terminal 2: Run the client
uv run streamlit run weather_assistant/client.py
```

## Project Structure

```
.
├── weather_assistant/
│   ├── __init__.py
│   ├── server.py           # MCP server with tracing
│   ├── client.py           # MCP client with context propagation
│   ├── config/
│   │   └── tracing.py      # OpenTelemetry and Langfuse setup
│   └── utils/
│       └── otel_utils.py   # Context propagation utilities
├── examples/
│   └── simple_client.py    # Minimal example
├── pyproject.toml          # Project dependencies and metadata
├── .env.example
└── docker-compose.yml      # For local development
```

## Key Concepts

### Why `_meta` Field Instead of HTTP Headers?

This implementation uses the MCP protocol's `_meta` field for trace context propagation. This approach:

- **Transport Agnostic**: Works with stdio, HTTP, and SSE transports
- **Standard Convention**: Follows the emerging MCP standard for metadata propagation ([PR #414](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/414))
- **W3C Compatible**: Uses W3C Trace Context (traceparent, tracestate, baggage)
- **Interoperable**: Compatible with `openinference-instrumentation-mcp` and other MCP tracing tools

### Decorator Stack

The key to proper context propagation is the decorator order on MCP tools:

```python
@mcp.tool()
@otel_utils.with_otel_context_from_meta
@observe
async def get_weather(location: str, _meta: dict | None = None) -> dict:
    # Your tool implementation
```

1. `@mcp.tool()` - Registers as MCP tool
2. `@with_otel_context_from_meta` - Extracts OTel context from MCP `_meta` field
3. `@observe` - Creates Langfuse span within the context

### Context Propagation Flow

**Client Side:**
```python
from weather_assistant.utils.otel_utils import inject_otel_context_to_meta

# Inject trace context into _meta field
meta = inject_otel_context_to_meta()

# Pass _meta to tool call
await client.call_tool("get_weather", {
    "location": "New York",
    "_meta": meta
})
```

**JSON-RPC Message Structure:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "New York"
    },
    "_meta": {
      "traceparent": "00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01",
      "tracestate": "...",
      "baggage": "..."
    }
  }
}
```

**Server Side:**
The `@with_otel_context_from_meta` decorator extracts context from `_meta` and activates it, then Langfuse's `@observe` creates spans within the propagated context.

## Monitoring

- **Langfuse Dashboard**: http://localhost:3000
  - View traces, token usage, costs, and latencies
  - See the complete request flow with proper parent-child relationships

## Development

### Setting up pre-commit hooks

```bash
uv sync --dev
uv run pre-commit install
```

This will install and configure pre-commit hooks that run:
- Ruff for linting and formatting
- Basic file checks (trailing whitespace, YAML syntax, etc.)
- MyPy for type checking

## Comparison: HTTP Headers vs `_meta` Field

| Aspect | HTTP Headers | `_meta` Field |
|--------|-------------|---------------|
| Transport Support | HTTP only | All transports (stdio, HTTP, SSE) |
| Standard | W3C Trace Context | MCP + W3C Trace Context |
| Implementation | Transport-specific | Protocol-level |
| Compatibility | HTTP libraries | Any MCP client/server |
| Use Case | HTTP-only deployments | Universal MCP applications |

## References

- [MCP Specification - `_meta` field convention](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/414)
- [OpenTelemetry Context Propagation](https://opentelemetry.io/docs/concepts/context-propagation/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [OpenInference MCP Instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-mcp)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for the excellent MCP framework
- [Langfuse](https://langfuse.com) for LLM observability
- [OpenTelemetry](https://opentelemetry.io) for distributed tracing standards
