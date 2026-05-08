from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.models import Lead
from app.schemas.schemas import AIAssessment
import json

anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def run_ai_assessment(lead: Lead, context_notes: str = "") -> dict:
    """
    Generate a full AI Opportunity Assessment for a lead.
    Returns structured JSON with scores, ROI, phases.
    """
    lead_context = f"""
Company: {lead.company_name}
Industry: {lead.industry}
Company size: {lead.company_size}
Country: {lead.country}
Contact: {lead.first_name} {lead.last_name}, {lead.title}
Estimated deal value: €{lead.estimated_value:,.0f}
Notes: {lead.notes or "None"}
Additional context: {context_notes or "None"}
"""

    system = """You are an AI automation consultant at NordKraft AI, a Nordic AI agency.
Your job is to assess how ready a company is for AI automation and what ROI they can expect.
Return ONLY valid JSON matching this schema exactly:
{
  "ai_score": <0-100 overall lead quality>,
  "automation_readiness": <0-100 readiness to adopt automation>,
  "ai_maturity_level": <1-5 where 1=beginner 5=advanced>,
  "estimated_time_savings_hrs": <integer hours per year>,
  "estimated_roi_multiplier": <float e.g. 4.8>,
  "key_opportunities": ["opportunity 1", "opportunity 2", "opportunity 3"],
  "recommended_phases": [
    {
      "phase": 1,
      "name": "Quick wins",
      "duration_weeks": "4-6",
      "description": "...",
      "deliverables": ["...", "..."],
      "estimated_cost_eur_min": 4000,
      "estimated_cost_eur_max": 6000
    }
  ],
  "summary": "2-3 sentence executive summary"
}"""

    message = await anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": f"Assess this company:\n{lead_context}"}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


async def generate_proposal(lead: Lead, assessment: dict, tone: str = "professional") -> dict:
    """Generate a full sales proposal as structured JSON."""

    system = """You are a senior sales consultant at NordKraft AI.
Generate a compelling, tailored sales proposal. Return ONLY valid JSON:
{
  "title": "...",
  "executive_summary": "...",
  "problem_statement": "...",
  "proposed_solution": "...",
  "phases": [{"phase": 1, "name": "...", "description": "...", "duration": "...", "investment": "..."}],
  "roi_section": {
    "time_savings_hrs_per_year": 0,
    "roi_multiplier": 0.0,
    "payback_period_months": 0,
    "narrative": "..."
  },
  "why_nordkraft": "...",
  "next_steps": ["...", "...", "..."],
  "total_investment_min": 0,
  "total_investment_max": 0,
  "currency": "EUR"
}"""

    context = f"""
Lead: {lead.first_name} {lead.last_name} at {lead.company_name} ({lead.industry})
Assessment: {json.dumps(assessment, indent=2)}
Tone: {tone}
"""

    message = await anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": context}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


async def generate_follow_up_email(lead: Lead, context: str = "", tone: str = "friendly_professional") -> dict:
    """Generate a personalised follow-up email."""

    system = """You are a sales rep at NordKraft AI.
Write a concise, warm, personalised follow-up email.
Return ONLY valid JSON:
{
  "subject": "...",
  "body": "..."
}
The body should be plain text, max 200 words, no markdown."""

    prompt = f"""
Contact: {lead.first_name} {lead.last_name}, {lead.title} at {lead.company_name}
Industry: {lead.industry}, Country: {lead.country}
AI Score: {lead.ai_score}, ROI estimate: {lead.estimated_roi_multiplier}x
Pipeline stage: {lead.status}
Context / call notes: {context or "No specific context"}
Tone: {tone}
"""

    message = await anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


async def summarise_meeting(transcript: str, lead_or_client_name: str) -> dict:
    """Extract summary + tasks from a meeting transcript."""

    system = """You are an AI assistant at NordKraft AI.
Summarise a sales or client meeting and extract action items.
Return ONLY valid JSON:
{
  "summary": "3-5 sentence summary",
  "key_decisions": ["...", "..."],
  "action_items": [
    {"title": "...", "owner": "...", "due": "ASAP|This week|Next week|TBD"},
    ...
  ],
  "sentiment": "positive|neutral|negative",
  "next_meeting_suggested": true
}"""

    message = await anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        system=system,
        messages=[{
            "role": "user",
            "content": f"Meeting with {lead_or_client_name}:\n\n{transcript}"
        }],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


async def ai_chat(message: str, history: list, context_type: str, context_data: dict = None) -> str:
    """General AI assistant chat for the CRM knowledge panel."""

    system = f"""You are the AI assistant inside NordKraft AI's internal CRM.
You help the sales and operations team with:
- Lead qualification and scoring advice
- Proposal writing and objection handling
- Client health analysis
- Automation recommendations
- Retrieving patterns from past projects
Context type: {context_type}
Context data: {json.dumps(context_data or {}, indent=2)}
Be concise, practical, and Nordic-direct. No fluff."""

    messages = history + [{"role": "user", "content": message}]

    response = await anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        system=system,
        messages=messages,
    )

    return response.content[0].text
