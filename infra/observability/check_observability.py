"""Smoke bout en bout : OTLP HTTP -> Collector -> Prometheus + Grafana."""

from __future__ import annotations

import json
import time
import urllib.request


def request_json(url: str, *, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=body)
    request.add_header("Accept", "application/json")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=5) as response:
        assert response.status == 200, (url, response.status)
        content = response.read().decode("utf-8")
        return json.loads(content) if content else {}


def eventually(run, *, timeout: float = 45.0) -> object:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            return run()
        except (AssertionError, OSError) as error:
            last_error = error
            time.sleep(2)
    raise AssertionError(f"service indisponible après {timeout:.0f}s: {last_error}")


def main() -> None:
    health = eventually(lambda: request_json("http://127.0.0.1:13133/"))
    assert health.get("status") == "Server available", health

    grafana = eventually(lambda: request_json("http://127.0.0.1:3001/api/health"))
    assert grafana.get("database") == "ok", grafana

    now = str(time.time_ns())
    request_json(
        "http://127.0.0.1:4318/v1/metrics",
        payload={
            "resourceMetrics": [
                {
                    "resource": {
                        "attributes": [
                            {
                                "key": "service.name",
                                "value": {"stringValue": "afrosite-smoke"},
                            }
                        ]
                    },
                    "scopeMetrics": [
                        {
                            "scope": {"name": "infra-smoke"},
                            "metrics": [
                                {
                                    "name": "afrosite_smoke_value",
                                    "gauge": {
                                        "dataPoints": [
                                            {
                                                "timeUnixNano": now,
                                                "asDouble": 1,
                                            }
                                        ]
                                    },
                                }
                            ],
                        }
                    ],
                }
            ]
        },
    )

    def assert_prometheus_targets() -> list[dict]:
        response = request_json("http://127.0.0.1:9090/api/v1/targets")
        targets = response["data"]["activeTargets"]
        expected = {"otel-collector", "afrosite-otlp-metrics"}
        healthy = {target["labels"]["job"] for target in targets if target.get("health") == "up"}
        assert expected <= healthy, (expected, healthy)
        return targets

    targets = eventually(assert_prometheus_targets)

    def assert_smoke_metric() -> str:
        response = request_json("http://127.0.0.1:9090/api/v1/label/__name__/values")
        names = response["data"]
        matches = [name for name in names if name.endswith("smoke_value")]
        assert matches, names
        return matches[0]

    metric = eventually(assert_smoke_metric)
    print(
        "check:observability OK - collector healthy - OTLP HTTP reçu - "
        f"Prometheus {len(targets)} cibles UP - métrique {metric} - Grafana DB ok"
    )


if __name__ == "__main__":
    main()
