"""Instrumentation FastAPI sans collector réel ni secret."""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import SpanKind

from afrosite_api.observability import configure_telemetry


class OTLPHandler(BaseHTTPRequestHandler):
    requests: list[tuple[str, str, int]] = []

    def do_POST(self) -> None:  # noqa: N802 - méthode imposée par la stdlib
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self.requests.append((self.path, self.headers.get("Content-Type", ""), len(body)))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *_args: object) -> None:
        return


def test_telemetry_is_opt_in() -> None:
    app = FastAPI()

    assert configure_telemetry(app, env={}) is None
    assert (
        configure_telemetry(
            app,
            env={
                "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector:4318",
                "OTEL_SDK_DISABLED": "true",
            },
        )
        is None
    )


def test_fastapi_request_exports_standard_server_span() -> None:
    app = FastAPI()

    @app.get("/ping")
    async def ping() -> dict[str, bool]:
        return {"ok": True}

    exporter = InMemorySpanExporter()
    telemetry = configure_telemetry(
        app,
        env={
            "OTEL_SERVICE_NAME": "afrosite-api-test",
        },
        span_exporter=exporter,
    )
    assert telemetry is not None

    with TestClient(app) as client:
        response = client.get("/ping")

    assert response.status_code == 200
    assert telemetry.force_flush()
    server_spans = [span for span in exporter.get_finished_spans() if span.kind is SpanKind.SERVER]
    assert len(server_spans) == 1
    span = server_spans[0]
    assert span.name == "GET /ping"
    # OTel Python bascule progressivement des anciens vers les nouveaux noms
    # de conventions sémantiques ; les deux restent standards.
    assert (
        span.attributes.get("http.request.method") or span.attributes.get("http.method")
    ) == "GET"
    assert (
        span.attributes.get("http.response.status_code") or span.attributes.get("http.status_code")
    ) == 200
    assert span.resource.attributes["service.name"] == "afrosite-api-test"
    telemetry.shutdown()


def test_health_route_is_excluded_from_traces() -> None:
    app = FastAPI()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    exporter = InMemorySpanExporter()
    telemetry = configure_telemetry(app, env={}, span_exporter=exporter)
    assert telemetry is not None

    with TestClient(app) as client:
        assert client.get("/health").status_code == 200

    assert telemetry.force_flush()
    assert exporter.get_finished_spans() == ()
    telemetry.shutdown()


def test_otlp_http_export_uses_standard_traces_endpoint() -> None:
    OTLPHandler.requests.clear()
    server = HTTPServer(("127.0.0.1", 0), OTLPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        app = FastAPI()

        @app.get("/ping")
        async def ping() -> dict[str, bool]:
            return {"ok": True}

        telemetry = configure_telemetry(
            app,
            env={
                "OTEL_EXPORTER_OTLP_ENDPOINT": (f"http://127.0.0.1:{server.server_port}"),
                "OTEL_SERVICE_NAME": "afrosite-api-http-test",
            },
        )
        assert telemetry is not None
        with TestClient(app) as client:
            assert client.get("/ping").status_code == 200
        assert telemetry.force_flush()
        telemetry.shutdown()
    finally:
        server.shutdown()
        server.server_close()

    assert len(OTLPHandler.requests) == 1
    path, content_type, body_size = OTLPHandler.requests[0]
    assert path == "/v1/traces"
    assert content_type == "application/x-protobuf"
    assert body_size > 0
