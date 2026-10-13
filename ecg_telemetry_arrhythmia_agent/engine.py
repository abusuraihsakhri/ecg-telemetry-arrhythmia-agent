"""
Clinical Algorithmic Engine & Guideline Rules for TelePulse: Autonomous Inpatient Continuous Telemetry Arrhythmia Supervisor.
Domain: Cardiology
Standard: Demonstration thresholds (not clinically validated)
"""
from typing import Dict, Any, List, Optional
from .models import ClinicalCasePayload, AgentAlert, UrgencyLevel, ClinicalIntegrityStatus


class ClinicalDomainEngine:
    GUIDELINE = "Demonstration thresholds (not clinically validated)"
    PRIMARY_BASELINE_LIMIT = 20.0
    SECONDARY_ALERT_LIMIT = 10.0

    @classmethod
    def evaluate_primary_index(cls, value: float) -> Optional[Dict[str, Any]]:
        if value > cls.PRIMARY_BASELINE_LIMIT:
            return {
                "title": "Primary Metric Threshold Exceeded",
                "finding": f"Observed value ({value:.2f}) exceeds demonstration threshold ({cls.PRIMARY_BASELINE_LIMIT:.1f}); units are not specified.",
                "recommendation": "Review the synthetic metric and its units; no arrhythmia diagnosis is made.",
            }
        return None

    @classmethod
    def evaluate_secondary_kinetics(cls, value: float, is_stat: bool) -> Optional[Dict[str, Any]]:
        if value > cls.SECONDARY_ALERT_LIMIT or is_stat:
            return {
                "title": "Secondary Metric or STAT Flag Triggered",
                "finding": f"Secondary metric ({value:.2f}) or synthetic STAT={is_stat} triggered a demonstration rule.",
                "recommendation": "Inspect the test input; this demonstration does not initiate clinical escalation.",
            }
        return None

    @classmethod
    def evaluate_biomarker_concordance(cls, status_flag: str, biomarkers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        status_upper = str(status_flag).upper()
        if "DISCORDANT" in status_upper or "EQUIVOCAL" in status_upper or "MUTANT" in status_upper:
            return {
                "title": "Status Descriptor Match",
                "finding": f"Status flag '{status_flag}' matched a demonstration descriptor rule.",
                "recommendation": f"Review the synthetic status descriptor; no clinical testing is recommended.",
            }
        return None
