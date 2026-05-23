from datetime import datetime
from typing import Any

from app.models.models import Lead


def apply_ai_assessment(lead: Lead, assessment: dict[str, Any]) -> None:
    lead.ai_score = assessment["ai_score"]
    lead.automation_readiness = assessment["automation_readiness"]
    lead.ai_maturity_level = assessment["ai_maturity_level"]
    lead.estimated_time_savings_hrs = assessment["estimated_time_savings_hrs"]
    lead.estimated_roi_multiplier = assessment["estimated_roi_multiplier"]
    lead.ai_assessment_json = assessment
    lead.last_assessed_at = datetime.utcnow()
