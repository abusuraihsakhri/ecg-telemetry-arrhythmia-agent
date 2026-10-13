"""API smoke tests exercise the two existing Python HTTP entry points."""
import os

os.environ.setdefault("AUDIT_SECRET_KEY", "pytest-only-ephemeral-audit-key")

from fastapi.testclient import TestClient

from agents.api import app as generic_app
from ecg_telemetry_arrhythmia_agent.server import create_app


def test_generic_audit_endpoint_and_hmac_verification():
    client = TestClient(generic_app)
    assert client.get("/health").status_code == 200
    response = client.post("/api/audit", json={
        "task_id": "SYNTH-API-001",
        "target_identifier": "SYNTH-TARGET-001",
        "primary_metric": 30,
        "secondary_metric": 2,
        "is_critical_flag": False,
        "status_descriptor": "NOMINAL",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["overall_urgency"] == "ELEVATED_RISK"
    assert len(result["audit_hash"]) == 64
    assert client.get("/api/audit/logs").json()["verified"] is True
    assert client.get("/metrics").status_code == 200


def test_package_api_rejects_nonfinite_metrics():
    app = create_app()
    assert app is not None
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    normal = client.post("/api/audit", json={
        "case_id": "CASE-001",
        "patient_synthetic_id": "SYNTH-001",
        "primary_metric": 15,
        "secondary_metric": 2,
        "status_flag": "NORMAL",
    })
    assert normal.status_code == 200
    assert normal.json()["overall_status"] == "CONCORDANT_NORMAL"
    invalid = client.post("/api/audit", content='{"primary_metric": NaN}', headers={"Content-Type": "application/json"})
    assert invalid.status_code == 422
