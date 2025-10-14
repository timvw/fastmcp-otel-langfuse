"""Streamlit client for weather assistant with distributed tracing."""

import streamlit as st
from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client import StreamableHttpTransport
from langfuse import observe
from opentelemetry import trace

from weather_assistant.config.tracing import setup_tracing
from weather_assistant.utils.otel_utils import inject_otel_context_to_meta

# Load environment variables
load_dotenv()

# Initialize tracing
langfuse_client = setup_tracing()
tracer = trace.get_tracer(__name__)


@observe
async def handle_weather_request(location: str, forecast_days: int = 3):
    """Handle weather request with distributed tracing."""

    # Inject trace context into _meta field
    meta = inject_otel_context_to_meta()

    # Create transport (no headers needed for trace propagation)
    transport = StreamableHttpTransport(url="http://localhost:8000/weather")

    async with Client(transport) as client:
        # Get current weather with _meta for trace propagation
        weather_result = await client.call_tool("get_weather", {"location": location, "_meta": meta})

        # Get forecast if requested
        forecast_result = None
        if forecast_days > 0:
            forecast_result = await client.call_tool("get_forecast", {"location": location, "days": forecast_days, "_meta": meta})

        return weather_result, forecast_result


# Streamlit UI
st.title("🌤️ Weather Assistant")

# User input
location = st.text_input("Enter city name:", "San Francisco")
forecast_days = st.slider("Forecast days:", 0, 7, 3)

if st.button("Get Weather"):
    with st.spinner("Fetching weather data..."):
        # Create a root span for the entire operation
        with tracer.start_as_current_span("weather_request") as span:
            span.set_attribute("location", location)
            span.set_attribute("forecast_days", forecast_days)

            try:
                import asyncio

                # Run the async function
                weather, forecast = asyncio.run(handle_weather_request(location, forecast_days))

                # Handle FastMCP response format - CallToolResult has content attribute
                import json

                if hasattr(weather, "content"):
                    # Extract content from CallToolResult
                    content = weather.content[0] if weather.content else None
                    if content and hasattr(content, "text"):
                        weather_data = json.loads(content.text)
                    else:
                        weather_data = weather
                else:
                    weather_data = weather

                # Display current weather
                st.subheader(f"Current Weather in {location}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Temperature", f"{weather_data['temperature']}°C")
                with col2:
                    st.metric("Condition", weather_data["condition"])
                with col3:
                    st.metric("Humidity", f"{weather_data['humidity']}%")

                # Display forecast if requested
                if forecast and forecast_days > 0:
                    # Handle FastMCP response format for forecast
                    if hasattr(forecast, "content"):
                        # Extract content from CallToolResult
                        content = forecast.content[0] if forecast.content else None
                        if content and hasattr(content, "text"):
                            forecast_data = json.loads(content.text)
                        else:
                            forecast_data = forecast
                    else:
                        forecast_data = forecast

                    st.subheader(f"{forecast_days}-Day Forecast")
                    for day_forecast in forecast_data:
                        with st.expander(f"Day {day_forecast['day']}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"High: {day_forecast['high']}°C")
                                st.write(f"Low: {day_forecast['low']}°C")
                            with col2:
                                st.write(f"Condition: {day_forecast['condition']}")
                            with col3:
                                st.write(f"Rain chance: {day_forecast['precipitation_chance']}%")

            except Exception as e:
                st.error(f"Error fetching weather: {str(e)}")
                span.record_exception(e)
                span.set_status(trace.StatusCode.ERROR)
