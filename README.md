# Closira AI Agent — Bloom Aesthetics Clinic

> AI-powered customer support workflow built for the Closira internship assignment.  
> Built with: **Groq (Llama 3.3 70B)** · **FastAPI** · **Vanilla HTML/CSS/JS**

---

## What This Does

A 4-stage AI customer support workflow:

| Stage | Description |
|---|---|
| **FAQ Answering** | Answers inbound questions strictly from the Bloom Aesthetics SOP |
| **Lead Qualification** | Collects business type, team size, and current tools |
| **Escalation Detection** | Detects angry sentiment, out-of-scope queries, medical/pricing questions |
| **Conversation Summary** | Generates structured end-of-session summary with intent, gaps, and next action |

---

## Project Structure

```
closira/
├── backend/
│   ├── main.py              # FastAPI app — all 4 stages
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── index.html           # Chat UI (no framework, pure HTML/CSS/JS)
├── test_transcripts/
│   └── all_scenarios.md     # 5 test scenarios with expected outputs
├── prompt_design.md         # Full prompt design document
└── README.md
```

---

## Setup

### 1. Get a Groq API Key
Sign up free at [console.groq.com](https://console.groq.com) and create an API key.

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the server
GROQ_API_KEY=your_key_here uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`

### 3. Frontend Setup

No build step needed. Just open:

```bash
open frontend/index.html
# or double-click index.html in your file explorer
```

On first load, enter your backend URL (`http://localhost:8000`) and click Connect.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Send a message, get AI response |
| `POST` | `/summary` | Generate session summary |
| `GET` | `/sop` | View the SOP data |
| `GET` | `/` | Health check |

### Chat Request Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your Botox prices?",
    "conversation_history": [],
    "session_id": "test_001",
    "lead_data": {}
  }'
```

### Response

```json
{
  "message": "Botox treatments at Bloom Aesthetics start from £200...",
  "stage": "faq",
  "escalate": false,
  "escalation_reason": null,
  "lead_data": {},
  "confidence": "high",
  "timestamp": "2026-05-24T10:00:00"
}
```

---

## SOP Data

The AI operates on this data only:

- **Business:** Bloom Aesthetics Clinic
- **Hours:** Mon–Sat, 9 AM–7 PM
- **Services:** Botox (£200+), Fillers (£250+), Consultations (free)
- **Booking:** WhatsApp or website · 24hr cancellation policy
- **Escalate if:** complaint, medical question, pricing negotiation, 2+ unanswered questions

---

## Escalation Logging

All escalations are logged to `backend/logs/escalations.jsonl`:

```json
{"session_id": "session_123", "timestamp": "...", "trigger_message": "...", "reason": "angry_sentiment"}
```

---

## Model Used

**Groq — `llama-3.3-70b-versatile`**
- Ultra-fast inference (< 1s response time)
- 128K context window
- Free tier available on Groq Console

---

## Trade-offs & Limitations

- **Stateless by design:** Conversation history passed per request. No DB required, but history resets if browser refreshes.
- **SOP in prompt:** Simple and effective for small SOPs. For 10,000+ token SOPs, add Qdrant vector search retrieval.
- **No auth:** This is a prototype. Production would add API key auth to the FastAPI endpoints.
- **JSON parsing fallback:** If the model wraps output in markdown fences, the backend strips and re-parses.

---

## Author

Built for Breakout (Closira) AI Engineering Internship Assignment — May 2026.
