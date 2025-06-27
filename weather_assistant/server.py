"""FastMCP server for weather assistant with distributed tracing."""

import random
from typing import Annotated

from dotenv import load_dotenv
from fastmcp import FastMCP
from langfuse import observe
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from weather_assistant.config.tracing import setup_tracing
from weather_assistant.utils import otel_utils

# Load environment variables
load_dotenv()

# Initialize tracing
setup_tracing()

# Initialize OpenTelemetry logging instrumentation
LoggingInstrumentor().instrument()

mcp = FastMCP()


@mcp.tool()
@otel_utils.with_otel_context_from_headers
@observe
async def get_weather(
    location: Annotated[str, "City name to get weather for"],
) -> Annotated[dict, "Current weather information"]:
    """
    Get current weather for a specified location.

    The decorator stack ensures:
    1. @mcp.tool() registers this as an MCP tool
    2. @with_otel_context_from_headers extracts trace context from HTTP headers
    3. @observe creates a Langfuse span within the OTel context
    """
    # Simulate weather API call
    weather_conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]

    return {
        "location": location,
        "temperature": random.randint(15, 30),
        "condition": random.choice(weather_conditions),
        "humidity": random.randint(40, 80),
        "wind_speed": random.randint(5, 25),
    }


@mcp.tool()
@otel_utils.with_otel_context_from_headers
@observe
async def get_forecast(
    location: Annotated[str, "City name for forecast"],
    days: Annotated[int, "Number of days to forecast (1-7)"] = 3,
) -> Annotated[list, "Weather forecast for the specified days"]:
    """Get weather forecast for the specified location and number of days."""
    forecast = []
    for day in range(1, min(days + 1, 8)):
        forecast.append(
            {
                "day": day,
                "high": random.randint(20, 35),
                "low": random.randint(10, 20),
                "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Stormy"]),
                "precipitation_chance": random.randint(0, 100),
            }
        )

    return forecast


if __name__ == "__main__":
    print("Starting Weather Assistant MCP Server on http://0.0.0.0:8000")
    print("Streamable HTTP endpoint available at http://localhost:8000/weather")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/weather")
