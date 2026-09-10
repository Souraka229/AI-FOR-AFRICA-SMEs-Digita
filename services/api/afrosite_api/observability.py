"""Instrumentation OpenTelemetry standard de l'API FastAPI."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from fastapi import FastAPI
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import (
    SERVICE_NAME,
    SERVICE_VERSION,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter


@dataclass(frozen=True)
class Telemetry:
    """Handle explicite pour vider ou arrêter proprement l'exporteur."""

    provider: TracerProvider

    def force_flush(self, timeout_millis: int = 5_000) -> bool:
        return self.provider.force_flush(timeout_millis)

    def shutdown(self) -> None:
        self.provider.shutdown()


def configure_telemetry(
    app: FastAPI,
    *,
    env: Mapping[str, str] | None = None,
    span_exporter: SpanExporter | None = None,
) -> Telemetry | None:
    """Instrumente ``app`` si un endpoint OTLP est configuré.

    L'exporteur injectable garde les tests sans réseau. En runtime, le client
    officiel utilise le endpoint OTLP standard fourni par l'environnement.
    """

    settings = env if env is not None else os.environ
    disabled = settings.get("OTEL_SDK_DISABLED", "").lower() in {"1", "true", "yes"}
    endpoint = settings.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    traces_endpoint = settings.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "").strip()
    if disabled or (not endpoint and not traces_endpoint and span_exporter is None):
        return None

    resource = Resource.create(
        {
            SERVICE_NAME: settings.get("OTEL_SERVICE_NAME", "afrosite-api"),
            SERVICE_VERSION: "0.1.0",
        }
    )
    provider = TracerProvider(resource=resource)
    exporter = span_exporter
    if exporter is None:
        exporter_endpoint = traces_endpoint or f"{endpoint.rstrip('/')}/v1/traces"
        exporter = OTLPSpanExporter(endpoint=exporter_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=provider,
        excluded_urls=r"/health$",
    )
    return Telemetry(provider=provider)
