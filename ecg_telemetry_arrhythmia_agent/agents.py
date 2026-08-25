"""
Distributed Component Hierarchy & Executive Coordinator for TelePulse: Autonomous Inpatient Continuous Telemetry Arrhythmia Supervisor.
Domain: Cardiology
"""
import uuid
from typing import Dict, Any, List, Optional
from .models import ClinicalCasePayload, AgentAlert, UrgencyLevel, ClinicalIntegrityStatus
from .engine import ClinicalDomainEngine


class RRPauseDetectorAgent:
    """Sub-Agent 1: Primary Metric & Baseline Quality Auditor."""
    def audit(self, case: ClinicalCasePayload) -> List[AgentAlert]:
        alerts = []
        res = ClinicalDomainEngine.evaluate_primary_index(case.primary_metric)
        if res:
            alerts.append(AgentAlert(
                alert_id=str(uuid.uuid4())[:8],
                sub_agent="RRPauseDetectorAgent",
                urgency=UrgencyLevel.WARNING,
                title=res["title"],
                clinical_finding=res["finding"],
                actionable_recommendation=res["recommendation"],
            ))
        return alerts


class EctopyFrequencyAgent:
    """Sub-Agent 2: STAT Kinetics & Closed-Loop Escalation Auditor."""
    def audit(self, case: ClinicalCasePayload) -> List[AgentAlert]:
        alerts = []
        res = ClinicalDomainEngine.evaluate_secondary_kinetics(case.secondary_metric, case.is_stat)
        if res:
            alerts.append(AgentAlert(
                alert_id=str(uuid.uuid4())[:8],
                sub_agent="EctopyFrequencyAgent",
                urgency=UrgencyLevel.STAT_CRITICAL if case.is_stat else UrgencyLevel.WARNING,
                title=res["title"],
                clinical_finding=res["finding"],
                actionable_recommendation=res["recommendation"],
            ))
        return alerts


class QTcDriftTrackerAgent:
    """Sub-Agent 3: Biomarker & Concordance Triager."""
    def audit(self, case: ClinicalCasePayload) -> List[AgentAlert]:
        alerts = []
        res = ClinicalDomainEngine.evaluate_biomarker_concordance(case.status_flag, case.biomarkers)
        if res:
            alerts.append(AgentAlert(
                alert_id=str(uuid.uuid4())[:8],
                sub_agent="QTcDriftTrackerAgent",
                urgency=UrgencyLevel.ADVISORY,
                title=res["title"],
                clinical_finding=res["finding"],
                actionable_recommendation=res["recommendation"],
            ))
        return alerts


class TelemetryCoordinator:
    """Executive Coordinator & Air-Gapped Supervisory Interface."""
    def __init__(self):
        self.agent_1 = RRPauseDetectorAgent()
        self.agent_2 = EctopyFrequencyAgent()
        self.agent_3 = QTcDriftTrackerAgent()
        self.case_registry: Dict[str, Dict[str, Any]] = {}

    def process_case(self, case: ClinicalCasePayload) -> Dict[str, Any]:
        all_alerts: List[AgentAlert] = []
        all_alerts.extend(self.agent_1.audit(case))
        all_alerts.extend(self.agent_2.audit(case))
        all_alerts.extend(self.agent_3.audit(case))

        stat_count = sum(1 for a in all_alerts if a.urgency == UrgencyLevel.STAT_CRITICAL)
        warn_count = sum(1 for a in all_alerts if a.urgency == UrgencyLevel.WARNING)

        if stat_count > 0:
            status = ClinicalIntegrityStatus.CRITICAL_ACTION_REQUIRED
        elif warn_count > 0 or all_alerts:
            status = ClinicalIntegrityStatus.DISCORDANCE_DETECTED
        else:
            status = ClinicalIntegrityStatus.CONCORDANT_NORMAL

        dossier = {
            "system": "ecg-telemetry-arrhythmia-agent",
            "domain": "Cardiology",
            "case_id": case.case_id,
            "patient_synthetic_id": case.patient_synthetic_id,
            "overall_status": status.value,
            "total_alerts": len(all_alerts),
            "stat_critical_alerts": stat_count,
            "warning_alerts": warn_count,
            "alerts": [a.to_dict() for a in all_alerts],
            "guideline_standard": "ACC / AHA / ASE Valvular & Telemetry Guidelines",
            "consensus_summary": f"Multi-agent supervision completed across 3 sub-agents with status [{status.value}].",
        }

        self.case_registry[case.case_id] = dossier
        return dossier

    def query_supervisory_chat(self, user_query: str) -> str:
        q = user_query.strip().lower()
        if "status" in q or "summary" in q:
            return f"TelePulse: Autonomous Inpatient Continuous Telemetry Arrhythmia Supervisor currently tracking {len(self.case_registry)} cases in on-premises memory."
        elif "guideline" in q or "standard" in q:
            return "Active clinical surveillance operates under ACC / AHA / ASE Valvular & Telemetry Guidelines validated protocols."
        else:
            return f"TelePulse: Autonomous Inpatient Continuous Telemetry Arrhythmia Supervisor executive agent online. Zero-PHI air-gapped monitoring active."
