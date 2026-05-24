from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI(title="Closira AI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── SOP Data ────────────────────────────────────────────────────────────────
SOP = {
    "business_name": "Bloom Aesthetics Clinic",
    "hours": "Monday to Saturday, 9 AM to 7 PM",
    "services": {
        "Botox": "Starting from £200",
        "Fillers": "Starting from £250",
        "Consultation": "Free of charge"
    },
    "booking": "Bookings can be made via WhatsApp or our website. A 24-hour cancellation notice is required.",
    "escalate_if": [
        "complaint",
        "medical question",
        "pricing negotiation",
        "more than 2 unanswered questions"
    ],
    "contact": "WhatsApp or website booking available"
}

SOP_TEXT = f"""
Business: {SOP['business_name']}
Working Hours: {SOP['hours']}
Services & Pricing:
- Botox: {SOP['services']['Botox']}
- Fillers: {SOP['services']['Fillers']}
- Consultation: {SOP['services']['Consultation']}
Booking Process: {SOP['booking']}
Escalation Required If: {', '.join(SOP['escalate_if'])}
"""

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = f"""You are Aria, a friendly and professional AI customer support assistant for Bloom Aesthetics Clinic.

YOUR KNOWLEDGE BASE (SOP):
{SOP_TEXT}

STRICT RULES:
1. ONLY answer questions using the SOP above. Do NOT invent prices, services, or policies.
2. If a question is NOT covered in the SOP, say: "I don't have that information right now. Let me connect you with our team." Then set escalate=true and is_unanswered=true.
3. If the customer seems angry, frustrated, or mentions a complaint, set escalate=true with reason "angry_sentiment".
4. If customer asks for pricing negotiation or medical advice, set escalate=true.
5. If you are unsure or low confidence, set escalate=true with reason "low_confidence".
6. If the customer asks more than 2 questions that are out-of-scope (not answered by SOP), you MUST set escalate=true with reason "too_many_unanswered_questions".
7. After collecting preferred treatment, prior experience with aesthetics, and availability, you have qualified the lead.

LEAD QUALIFICATION QUESTIONS (ask one at a time naturally if they are looking to book):
- Which treatment are you most interested in (e.g., Botox, Fillers, or a Consultation)?
- Have you ever had any aesthetic treatments before?
- What day or time works best for your appointment?

RESPONSE FORMAT - always reply with valid JSON only, no markdown fences:
{{
  "message": "Your response to the customer",
  "stage": "faq|qualification|escalation|summary",
  "escalate": false,
  "escalation_reason": null,
  "lead_data": {{}},
  "confidence": "high|medium|low",
  "is_unanswered": false
}}

TONE: Warm, professional, concise. Like a friendly clinic receptionist.
"""

# ─── Helper: call Groq API directly ──────────────────────────────────────────
def call_groq(messages: list, max_tokens: int = 600, temperature: float = 0.3) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def parse_json_response(raw: str) -> dict:
    """Safely parse JSON from model output, stripping markdown fences if needed."""
    text = raw.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except:
                continue
    try:
        return json.loads(text)
    except:
        # Fallback: return safe default structure if all parsing fails
        return {
            "message": text,
            "stage": "faq",
            "escalate": False,
            "escalation_reason": None,
            "lead_data": {},
            "confidence": "medium",
            "is_unanswered": False
        }


def log_escalation(session_id: str, message: str, reason: str):
    log = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "trigger_message": message,
        "reason": reason
    }
    os.makedirs("logs", exist_ok=True)
    with open("logs/escalations.jsonl", "a") as f:
        f.write(json.dumps(log) + "\n")
    print(f"[ESCALATION] {log}")


# ─── Models ──────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []
    session_id: str = "default"
    lead_data: dict = {}
    unanswered_count: int = 0

class SummaryRequest(BaseModel):
    conversation_history: list
    lead_data: dict = {}


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "Closira AI Agent is running", "version": "1.0.0"}


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        current_unanswered = req.unanswered_count

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in req.conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": req.message})

        if current_unanswered > 0:
            messages.append({
                "role": "system",
                "content": f"System Notice: The customer has already asked {current_unanswered} question(s) that were out of SOP scope."
            })

        raw = call_groq(messages)
        data = parse_json_response(raw)
        merged_lead = {**req.lead_data, **data.get("lead_data", {})}

        # Handle boolean variations from raw model output
        is_unanswered_flag = data.get("is_unanswered")
        if is_unanswered_flag in [True, "true", "True"]:
            current_unanswered += 1
        else:
            if not data.get("escalate"):
                current_unanswered = 0

        if current_unanswered > 2:
            data["escalate"] = True
            data["escalation_reason"] = "more than 2 unanswered questions"

        if data.get("escalate"):
            log_escalation(req.session_id, req.message, data.get("escalation_reason", "unknown"))

        return {
            "message": data.get("message", ""),
            "stage": data.get("stage", "faq"),
            "escalate": bool(data.get("escalate", False)),
            "escalation_reason": data.get("escalation_reason"),
            "lead_data": merged_lead,
            "confidence": data.get("confidence", "high"),
            "unanswered_count": current_unanswered,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summary")
async def generate_summary(req: SummaryRequest):
    try:
        conversation_text = "\n".join([
            f"{m['role'].upper()}: {m['content']}"
            for m in req.conversation_history
        ])

        prompt = f"""Based on this customer conversation, generate a structured summary.

CONVERSATION:
{conversation_text}

LEAD DATA COLLECTED:
{json.dumps(req.lead_data, indent=2)}

Return ONLY valid JSON with no markdown fences:
{{
  "customer_intent": "What the customer was looking for",
  "key_details": ["detail 1", "detail 2"],
  "sop_gaps": ["Any questions the AI could not answer from SOP"],
  "lead_qualified": true,
  "lead_summary": {{"treatment_interested": "", "prior_experience": "", "preferred_timing": ""}},
  "recommended_action": "Next step for the human agent",
  "sentiment": "positive|neutral|negative",
  "escalated": false
}}"""

        raw = call_groq([{"role": "user", "content": prompt}], temperature=0.2)
        summary = parse_json_response(raw)
        return summary

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sop")
def get_sop():
    return SOP