"""OpenTelemetry utilities for context propagation."""

import asyncio
import functools
from contextlib import contextmanager
from typing import Optional

from opentelemetry import trace
from opentelemetry.context import attach, detach
from opentelemetry.propagate import extract


@contextmanager
def with_otel_context(carrier: Optional[dict[str, str]] = None):
    """
    Context manager that extracts and activates OpenTelemetry context from carrier.
    """
    if carrier:
        # Extract context from carrier
        ctx = extract(carrier)
        # Attach the context
        token = attach(ctx)
        try:
            # Get current span from the attached context
            yield trace.get_current_span()
        finally:
            # Detach the context when done
            detach(token)
    else:
        # No carrier provided, just yield current span
        yield trace.get_current_span()


def with_otel_context_from_headers(func):
    """
    Decorator that extracts HTTP headers and establishes OpenTelemetry context.

    This decorator should be applied before @observe to ensure the context
    is available when Langfuse creates its spans.
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Import here to avoid circular dependency
        from fastmcp.server.dependencies import get_http_headers

        headers = get_http_headers()
        with with_otel_context(headers):
            return await func(*args, **kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Import here to avoid circular dependency
        from fastmcp.server.dependencies import get_http_headers

        headers = get_http_headers()
        with with_otel_context(headers):
            return func(*args, **kwargs)

    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
