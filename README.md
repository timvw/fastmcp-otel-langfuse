# FastMCP with OpenTelemetry and Langfuse

A complete example demonstrating distributed tracing in FastMCP applications using OpenTelemetry context propagation and Langfuse for LLM observability.

📝 **Blog Post**: [Distributed Tracing with FastMCP: Combining OpenTelemetry and Langfuse](https://timvw.be/2025/06/27/distributed-tracing-fastmcp-langfuse-opentelemetry/)

## Overview

This repository shows how to:
- Build MCP servers with proper distributed tracing
- Propagate OpenTelemetry context via HTTP headers
- Integrate Langfuse for LLM-specific observability
- Maintain trace hierarchy across client-server boundaries

## Features

- 🔍 **Distributed Tracing**: Seamless trace context propagation between MCP client and server
- 📊 **LLM Observability**: Track token usage, costs, and latencies with Langfuse
- 🎯 **Clean Architecture**: Decorator-based approach for minimal code intrusion
- 🐳 **Docker Ready**: Includes docker-compose setup for local development

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

### Decorator Stack

The key to proper context propagation is the decorator order on MCP tools:

```python
@mcp.tool()
@otel_utils.with_otel_context_from_headers
@observe
async def get_weather(location: str) -> dict:
    # Your tool implementation
```

1. `@mcp.tool()` - Registers as MCP tool
2. `@with_otel_context_from_headers` - Extracts OTel context from HTTP headers
3. `@observe` - Creates Langfuse span within the context

### Context Propagation

The client injects trace context into HTTP headers:
```python
carrier = {}
inject(carrier)  # OpenTelemetry context injection

transport = StreamableHttpTransport(
    url="http://localhost:8000/weather",
    headers=carrier
)
```

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for the excellent MCP framework
- [Langfuse](https://langfuse.com) for LLM observability
- [OpenTelemetry](https://opentelemetry.io) for distributed tracing standards
