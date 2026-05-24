# Test Transcripts — Closira AI Agent
# Bloom Aesthetics Clinic · Aria

---

## Transcript 1: In-SOP Question (Botox Prices)

**Scenario:** Customer asks about Botox pricing — AI must answer accurately from SOP only.

---

USER: Hi, what are your Botox prices?

ARIA: Hi there! 💫 Botox treatments at Bloom Aesthetics Clinic start from £200. The exact price may vary depending on the areas treated and the units required, which our specialists assess during your consultation.

The good news — consultations are completely free! Would you like to book one, or do you have any other questions?

**[stage: faq | escalate: false | confidence: high]**

---

USER: Are fillers more expensive?

ARIA: Fillers start from £250 at Bloom Aesthetics, so they're slightly higher than Botox. Both are priced based on the treatment areas and your individual needs, which is why we offer a free consultation first — so you get a personalised recommendation with no commitment.

Would you like to book a consultation?

**[stage: faq | escalate: false | confidence: high]**

---

## Transcript 2: Out-of-Scope Question

**Scenario:** Customer asks something not in the SOP — AI must acknowledge and escalate, not guess.

---

USER: Do you offer laser hair removal?

ARIA: That's a great question! I don't have information about laser hair removal in our current services list. I wouldn't want to give you inaccurate details — let me connect you with our team who can confirm exactly what we offer.

**[stage: faq | escalate: true | escalation_reason: out_of_scope | confidence: low]**

🔔 **Escalated to Human Agent** — Reason: out_of_scope

---

USER: What about skin peels or microneedling?

ARIA: I'm afraid I don't have those specific services in my current information. Rather than guessing, I'd recommend reaching out to our team directly via WhatsApp — they'll give you the full and accurate list of everything we offer.

**[stage: faq | escalate: true | escalation_reason: out_of_scope | confidence: low]**

---

## Transcript 3: Escalation Trigger (Angry Sentiment / Complaint)

**Scenario:** Customer expresses frustration — AI detects sentiment and escalates with reason logged.

---

USER: I'm really frustrated. I booked an appointment last week and no one called me back. This is completely unacceptable.

ARIA: I'm truly sorry to hear this — that's absolutely not the experience we want you to have, and I completely understand your frustration. This needs to be addressed by our team directly and urgently.

I'm flagging this right now and a team member will reach out to you as soon as possible to make this right. Again, I apologise sincerely for the inconvenience.

**[stage: escalation | escalate: true | escalation_reason: angry_sentiment | confidence: high]**

🔔 **Escalated to Human Agent** — Reason: angry_sentiment

---

USER: I want to make a formal complaint.

ARIA: Of course — you have every right to do so, and we take complaints very seriously. I'm immediately escalating this to our management team who will handle your complaint personally. You'll hear from us very shortly.

**[stage: escalation | escalate: true | escalation_reason: complaint | confidence: high]**

---

## Transcript 4: Lead Qualification

**Scenario:** AI asks structured clinic-specific questions to qualify a potential booking lead.

---

USER: Hi, I'm thinking about getting some treatment done.

ARIA: Hello! How lovely — you've come to the right place. 😊 To help point you in the right direction, could I ask: which treatment are you most interested in — Botox, Fillers, or would you like to start with a free Consultation?

**[stage: qualification | escalate: false | lead_data: {} | confidence: high]**

---

USER: I think Botox, but I'm not sure — I've never had anything done before.

ARIA: That's completely fine — a lot of our clients come in for the first time curious about Botox! It's actually a great idea to start with a free consultation so our specialist can walk you through exactly what to expect.

Just one more thing — what day or time tends to work best for you? We're open Monday to Saturday, 9 AM to 7 PM.

**[stage: qualification | escalate: false | lead_data: {treatment_interested: "Botox", prior_experience: "No previous treatments"} | confidence: high]**

---

USER: Weekends work best, preferably Saturday afternoon.

ARIA: Perfect! Here's a quick summary of what I've noted:

- **Treatment of interest:** Botox
- **Prior experience:** No previous treatments
- **Preferred timing:** Saturday afternoon

I'll pass this to our team so they can get a Saturday afternoon slot confirmed for you. You can also book directly via WhatsApp or our website. Is there anything else I can help you with?

**[stage: qualification | escalate: false | lead_data: {treatment_interested: "Botox", prior_experience: "No previous treatments", preferred_timing: "Saturday afternoon"} | confidence: high]**

---

## Transcript 5: Conversation Summary

**Scenario:** End of session — AI generates a structured summary via POST /summary.

---

*(After a full conversation covering FAQ + lead qualification)*

**POST /summary response:**

```json
{
  "customer_intent": "Customer inquired about Botox pricing and expressed interest in booking their first ever aesthetic treatment at Bloom Aesthetics Clinic.",
  "key_details": [
    "Interested in Botox (from £200)",
    "No prior aesthetic treatment experience",
    "Prefers Saturday afternoon appointments",
    "Free consultation recommended as first step"
  ],
  "sop_gaps": [],
  "lead_qualified": true,
  "lead_summary": {
    "treatment_interested": "Botox",
    "prior_experience": "No previous treatments",
    "preferred_timing": "Saturday afternoon"
  },
  "recommended_action": "Book a free Saturday afternoon consultation slot for the customer. Confirm via WhatsApp. Brief the specialist that this is a first-time client interested in Botox.",
  "sentiment": "positive",
  "escalated": false
}
```