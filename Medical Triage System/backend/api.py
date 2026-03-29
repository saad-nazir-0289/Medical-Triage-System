# -*- coding: utf-8 -*-
"""
FastAPI backend for Medical Triage System.
POST /diagnose - accepts patient input and session state, returns triage response.
"""

import os
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import triage_engine

app = FastAPI(
    title="Medical Triage API",
    description="AI-powered medical triage with flowchart-based decision support",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DiagnoseRequest(BaseModel):
    patient_input: str = Field(..., description="Patient's message (symptoms or answer to question)")
    language: str = Field(default="english", description="Detected language")
    conversation_history: Optional[list[dict[str, Any]]] = Field(default_factory=list)
    session_state: Optional[dict[str, Any]] = Field(default=None, description="Backend state for flowchart progress")


class DiagnoseResponse(BaseModel):
    response_text: str
    urgency_level: str = "NORMAL"
    triage_result: Optional[dict[str, Any]] = None
    next_question: Optional[str] = None
    reasoning: Optional[str] = None
    session_state: Optional[dict[str, Any]] = None


def _get_flowchart_by_id(fc_id: str):
    """Get flowchart dict by id from loaded flowcharts."""
    flowcharts = triage_engine._load_flowcharts()
    for fc in flowcharts:
        if fc["id"] == fc_id:
            return fc
    return None


@app.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(req: DiagnoseRequest):
    """
    Process patient input and return triage response.
    - First message (no session_state): Select flowchart from symptoms, return first question.
    - Subsequent messages: Process answer, return next question or final triage result.
    """
    try:
        session_state = req.session_state or {}
        patient_input = (req.patient_input or "").strip()

        if not patient_input:
            raise HTTPException(status_code=400, detail="patient_input is required")

        flowchart_id = session_state.get("flowchart_id")
        current_node_index = session_state.get("current_node_index")
        trace = session_state.get("trace")
        completed = session_state.get("completed", False)

        # Case 1: Starting new triage - no flowchart yet, or previous triage completed
        if not flowchart_id or current_node_index is None or completed:
            fc = triage_engine.select_flowchart_semantic(patient_input)
            nodes = list(fc["nodes"].items())
            if not nodes:
                return DiagnoseResponse(
                    response_text="No questions available for this scenario. Please consult a healthcare professional.",
                    urgency_level="NORMAL",
                    reasoning="Empty flowchart",
                    session_state={"flowchart_id": fc["id"], "current_node_index": 0, "trace": {
                        "selected_flowchart": {"id": fc["id"], "title": fc["title"], "scenario": fc["scenario"]},
                        "time": None, "qa": [], "red_flag": None, "final": None
                    }},
                )
            first_question = nodes[0][1]["question"]
            new_state = {
                "flowchart_id": fc["id"],
                "current_node_index": 0,
                "trace": {
                    "selected_flowchart": {"id": fc["id"], "title": fc["title"], "scenario": fc["scenario"]},
                    "time": str(datetime.now()),
                    "qa": [],
                    "red_flag": None,
                    "final": None,
                },
            }
            return DiagnoseResponse(
                response_text=f"I've identified your scenario: **{fc['title']}**. Please answer the following:\n\n{first_question}",
                urgency_level="NORMAL",
                next_question=first_question,
                reasoning=f"Selected flowchart: {fc['id']}",
                session_state=new_state,
            )

        # Case 2: Continuing triage - process answer to current question
        fc = _get_flowchart_by_id(flowchart_id)
        if not fc:
            raise HTTPException(status_code=400, detail=f"Flowchart {flowchart_id} not found")

        (
            response_text,
            urgency_level,
            triage_result,
            next_question,
            updated_trace,
            updated_state,
        ) = triage_engine.process_flowchart_step(
            fc, current_node_index, patient_input, trace
        )

        return DiagnoseResponse(
            response_text=response_text,
            urgency_level=urgency_level,
            triage_result=triage_result,
            next_question=next_question,
            reasoning="Flowchart step processed",
            session_state=updated_state,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.on_event("startup")
async def startup():
    """Optionally pre-load models on startup."""
    if os.environ.get("TRIAGE_PRELOAD_MODELS", "false").lower() != "true":
        return
    try:
        triage_engine.ensure_models_loaded()
    except Exception as e:
        # Don't fail startup - models will load on first request
        print(f"Warning: Could not pre-load models: {e}")
