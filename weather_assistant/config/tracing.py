"""Configure OpenTelemetry and Langfuse for the application."""

import os

from langfuse import Langfuse
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider


def setup_tracing():
    """Configure OpenTelemetry and Langfuse for the application."""

    # Check if TracerProvider is already set
    if trace.get_tracer_provider() is not trace.ProxyTracerProvider():
        # Tracing already initialized, just return Langfuse client
        return Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
        )

    # Configure OpenTelemetry
    resource = Resource.create(
        {
            "service.name": os.getenv("OTEL_SERVICE_NAME", "weather-assistant"),
            "service.version": "1.0.0",
        }
    )

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure Langfuse
    langfuse_client = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
    )

    return langfuse_client
