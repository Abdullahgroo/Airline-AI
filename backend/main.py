from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai_agent import process_user_message
from airline_data import FLIGHTS
from airline_tools import get_baggage_policy, get_flight_status


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = Field(default_factory=list)


app = FastAPI(title="Airline AI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Airline AI Agent API is running"}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "airline-ai-agent"}


@app.get("/api/flights")
def get_all_flights():
    return {"flights": FLIGHTS}


@app.get("/api/flights/{flight_number}")
def get_flight(flight_number: str):
    try:
        return {"flight": get_flight_status(flight_number)}
    except ValueError as exc:
        return {"error": str(exc)}


@app.get("/api/baggage/{airline}")
def get_airline_baggage(airline: str):
    return get_baggage_policy(airline)


@app.post("/api/chat")
def chat(request: ChatRequest):
    if not request.message or not str(request.message).strip():
        return {
            "response": "Please enter a valid message before sending.",
            "tool_used": None,
            "data": None,
        }

    return process_user_message(request.message, request.history)
