import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Lead, AdvisorSubmission

app = FastAPI(title="Flowlayers Website API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Flowlayers Backend Running"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# --------- Models for responses ---------
class AdvisorResult(BaseModel):
    estimated_monthly_savings: float
    estimated_roi: float
    recommendations: List[str]

# --------- Helper logic for advisor ---------

def compute_advisor_result(payload: AdvisorSubmission) -> AdvisorResult:
    # Simple heuristic model for demo purposes
    base_rate = 15.0  # minutes saved per process per day
    employees = payload.employees or 5
    processes = len(payload.key_processes or []) or 3
    time_saved_hours = base_rate * processes * 22 / 60.0  # workdays per month

    # Cost assumptions
    avg_hourly_cost = 10.0
    savings = time_saved_hours * avg_hourly_cost * employees

    # ROI estimation based on indicative implementation cost
    impl_cost = 1500.0
    roi = (savings * 12 - impl_cost) / max(impl_cost, 1)

    recs = []
    tools = [t.lower() for t in (payload.current_tools or [])]
    pains = [p.lower() for p in (payload.pain_points or [])]

    if "invoices" in " ".join(pains) or (payload.monthly_invoices or 0) > 100:
        recs.append("LaylEngine: OCR + ERP sync for invoices and expenses")
    if any(t in tools for t in ["whatsapp", "meta", "instagram", "facebook"]):
        recs.append("Multi-channel CRM with WhatsApp Business API and GPT replies")
    if "manual data entry" in pains or "sheets" in tools:
        recs.append("n8n automations to eliminate manual data entry across apps")
    if not recs:
        recs.append("Discovery workshop to map quick-win automations in 1 week")

    return AdvisorResult(
        estimated_monthly_savings=round(savings, 2),
        estimated_roi=round(roi, 2),
        recommendations=recs[:5]
    )

# --------- API: AI Automation Advisor ---------
@app.post("/advisor/submit", response_model=AdvisorResult)
def advisor_submit(payload: AdvisorSubmission):
    try:
        # Save submission for analytics
        try:
            create_document("advisorsubmission", payload)
        except Exception:
            pass
        # Compute result
        return compute_advisor_result(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --------- API: Leads (Contact form) ---------
@app.post("/lead")
def create_lead(lead: Lead):
    try:
        doc_id = create_document("lead", lead)
        return {"ok": True, "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
