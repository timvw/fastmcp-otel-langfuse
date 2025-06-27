"""Streamlit client for weather assistant with distributed tracing."""

import streamlit as st
from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client import StreamableHttpTransport
from langfuse import observe
from opentelemetry import trace
from opentelemetry.propagate import inject

from weather_assistant.config.tracing import setup_tracing

# Load environment variables
load_dotenv()

# Initialize tracing
langfuse_client = setup_tracing()
tracer = trace.get_tracer(__name__)


@observe
async def handle_weather_request(location: str, forecast_days: int = 3):
    """Handle weather request with distributed tracing."""

    # Prepare carrier for context propagation
    carrier: dict[str, str] = {}
    inject(carrier)

    # Create transport with trace context headers
    transport = StreamableHttpTransport(url="http://localhost:8000/weather", headers=carrier)

    async with Client(transport) as client:
        # Get current weather
        weather_result = await client.call_tool("get_weather", {"location": location})

        # Get forecast if requested
        forecast_result = None
        if forecast_days > 0:
            forecast_result = await client.call_tool("get_forecast", {"location": location, "days": forecast_days})

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

                # Handle FastMCP response format
                if isinstance(weather, list) and weather:
                    # FastMCP returns tool responses as a list of content objects
                    weather_data = weather[0]
                    if hasattr(weather_data, "text"):
                        import json

                        weather_data = json.loads(weather_data.text)
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
                    if isinstance(forecast, list) and forecast:
                        forecast_data = forecast[0]
                        if hasattr(forecast_data, "text"):
                            import json

                            forecast_data = json.loads(forecast_data.text)
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
