from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pickle
import numpy as np
import datetime
import json

app = FastAPI(title="AI Agent Honeypot Classifier API")

with open("classifier_model.pkl", "rb") as f:
    MODEL = pickle.load(f)

CLASSES = ["ai_agent", "bot", "human"]
FEATURES = [
    "response_time_ms", "trap_followed", "paths_visited",
    "avg_delay_ms", "unique_paths", "visited_api_keys",
    "visited_backup", "visited_config", "session_duration_s"
]

class Session(BaseModel):
    session_id: str = "unknown"
    response_time_ms: float = 0.0
    trap_followed: int = 0
    paths_visited: int = 1
    avg_delay_ms: float = 1000.0
    unique_paths: int = 1
    visited_api_keys: int = 0
    visited_backup: int = 0
    visited_config: int = 0
    session_duration_s: float = 10.0

@app.get("/")
async def home():
    return {
        "name": "AI Agent Honeypot Classifier",
        "version": "1.0",
        "endpoints": ["/classify", "/classify/bulk", "/health"],
        "classes": CLASSES
    }

@app.get("/health")
async def health():
    return {"status": "running", "model": "Random Forest", "classes": CLASSES}

@app.post("/classify")
async def classify(session: Session):
    features = np.array([[
        session.response_time_ms,
        session.trap_followed,
        session.paths_visited,
        session.avg_delay_ms,
        session.unique_paths,
        session.visited_api_keys,
        session.visited_backup,
        session.visited_config,
        session.session_duration_s
    ]])
    prediction = MODEL.predict(features)[0]
    probabilities = MODEL.predict_proba(features)[0]
    predicted_class = CLASSES[prediction]
    confidence = float(max(probabilities))
    result = {
        "session_id": session.session_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "prediction": predicted_class,
        "confidence": round(confidence, 4),
        "probabilities": {
            "ai_agent": round(float(probabilities[0]), 4),
            "bot": round(float(probabilities[1]), 4),
            "human": round(float(probabilities[2]), 4)
        },
        "alert": predicted_class == "ai_agent" and confidence > 0.7
    }
    print(f"[CLASSIFY] {session.session_id} → {predicted_class} ({confidence:.2%}) alert={result['alert']}")
    return JSONResponse(result)

@app.post("/classify/bulk")
async def classify_bulk(sessions: list[Session]):
    results = []
    for session in sessions:
        features = np.array([[
            session.response_time_ms,
            session.trap_followed,
            session.paths_visited,
            session.avg_delay_ms,
            session.unique_paths,
            session.visited_api_keys,
            session.visited_backup,
            session.visited_config,
            session.session_duration_s
        ]])
        prediction = MODEL.predict(features)[0]
        probabilities = MODEL.predict_proba(features)[0]
        predicted_class = CLASSES[prediction]
        confidence = float(max(probabilities))
        results.append({
            "session_id": session.session_id,
            "prediction": predicted_class,
            "confidence": round(confidence, 4),
            "alert": predicted_class == "ai_agent" and confidence > 0.7
        })
    ai_alerts = sum(1 for r in results if r["alert"])
    return JSONResponse({
        "total_sessions": len(results),
        "ai_agent_alerts": ai_alerts,
        "results": results
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
