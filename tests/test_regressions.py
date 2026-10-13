"""Regression tests for audit authenticity and synthetic telemetry rule inputs."""
import os
import math

import pytest

os.environ.setdefault("AUDIT_SECRET_KEY", "pytest-only-ephemeral-audit-key")

from agents.base import AuditTrail
from ecg_telemetry_arrhythmia_agent.models import ClinicalCasePayload
from tele_pulse import EctopyFrequencyAgent, RRPauseDetectorAgent, TelemetryCoordinator


def test_audit_trail_recomputes_signed_fields():
    trail = AuditTrail(secret_key="local-test-key")
    trail.log("worker", "supervisor", "TEST", {"status": "ok"})
    trail.log("worker", "supervisor", "NEXT", {"status": "ok"})
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "modified"
    assert not trail.verify_integrity()


def test_audit_trail_detects_signature_or_metadata_tampering():
    trail = AuditTrail(secret_key="local-test-key")
    trail.log("worker", "supervisor", "TEST", {"status": "ok"})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_audit_snapshot_is_not_a_mutable_ledger_reference():
    trail = AuditTrail(secret_key="local-test-key")
    trail.log("worker", "supervisor", "TEST", {"status": "ok"})
    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "modified"
    snapshot.append({"junk": True})
    assert len(trail.get_trail()) == 1
    assert trail.verify_integrity()


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_telepulse_numeric_validation(value):
    with pytest.raises(ValueError, match="finite"):
        RRPauseDetectorAgent().evaluate({"metric_primary": value})
    with pytest.raises(ValueError, match="finite"):
        EctopyFrequencyAgent().evaluate({"metric_secondary": value})
    with pytest.raises(ValueError, match="finite"):
        ClinicalCasePayload(
            case_id="CASE-01",
            patient_synthetic_id="SYNTH-01",
            primary_metric=value,
            secondary_metric=0,
            status_flag="NORMAL",
        )


def test_false_string_does_not_trigger_critical_alarm():
    agent = EctopyFrequencyAgent()
    assert agent.evaluate({"critical_flag": "False", "metric_secondary": 2.0}) == []
    assert len(agent.evaluate({"critical_flag": "True", "metric_secondary": 2.0})) == 1
    with pytest.raises(ValueError, match="boolean"):
        agent.evaluate({"critical_flag": "perhaps", "metric_secondary": 2.0})


def test_advisory_status_not_reported_as_normal():
    report = TelemetryCoordinator().audit_case({
        "case_id": "SYNTH-CASE",
        "metric_primary": 10.0,
        "metric_secondary": 2.0,
        "status_text": "DISCORDANT",
        "critical_flag": "false",
    })
    assert report["total_alerts"] == 1
    assert report["overall_status"] == "ADVISORY_ACTIVE"


def test_normal_status_remains_unchanged():
    report = TelemetryCoordinator().audit_case({
        "case_id": "SYNTH-CASE",
        "metric_primary": 10.0,
        "metric_secondary": 2.0,
        "status_text": "NORMAL",
        "critical_flag": False,
    })
    assert report["overall_status"] == "CONCORDANT_NORMAL"
