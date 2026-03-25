# -*- coding: utf-8 -*-
"""
Medical Triage Engine - Extracted from untitled15.py
FAISS + TinyLlama-based flowchart triage with semantic retrieval.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Lazy-loaded globals
_embedder = None
_llm = None
_FLOWCHARTS = None
_faiss_index = None

# Path resolution: flowcharts can be in parent dir or same dir as backend
def _get_flowcharts_path():
    base = Path(__file__).resolve().parent.parent
    candidates = [
        base / "triage_flowcharts_weighted.json",
        base.parent / "triage_flowcharts_weighted.json",
        Path("triage_flowcharts_weighted.json"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return str(base / "triage_flowcharts_weighted.json")


def _load_flowcharts():
    global _FLOWCHARTS
    if _FLOWCHARTS is None:
        path = _get_flowcharts_path()
        with open(path, "r", encoding="utf-8") as f:
            _FLOWCHARTS = json.load(f)
    return _FLOWCHARTS


def _load_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def _load_llm():
    global _llm
    if _llm is None:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL, torch_dtype=torch.float32, device_map="cpu"
        )
        _llm = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=40,
            do_sample=False
        )
    return _llm


def _build_faiss_index():
    global _faiss_index
    if _faiss_index is None:
        import faiss
        import numpy as np
        flowcharts = _load_flowcharts()
        embedder = _load_embedder()
        texts = []
        for fc in flowcharts:
            t = fc["title"] + " " + " ".join(fc.get("entry_keywords", []))
            texts.append(t)
        vecs = embedder.encode(texts)
        vecs = np.array(vecs).astype("float32")
        index = faiss.IndexFlatL2(vecs.shape[1])
        index.add(vecs)
        _faiss_index = index
    return _faiss_index


# Parse helpers
YES = ["yes", "haan", "yeah", "true", "yep", "sure", "of course"]
NO = ["no", "nah", "nope", "false", "not", "never"]


def parse_fast(ans):
    t = str(ans).lower()
    if any(x in t for x in YES):
        return "yes"
    if any(x in t for x in NO):
        return "no"
    return "unknown"


def llm_parse(q, a):
    llm = _load_llm()
    prompt = f"""
        You are a clinical language interpreter.

        Task:
        Decide if the patient's answer means YES or NO to the question.

        Rules:
        - "I don't think so" = NO
        - "probably not" = NO
        - "not really" = NO
        - "maybe" = UNKNOWN
        - If unclear, return UNKNOWN
        - DO NOT guess.
        - Return ONLY one word: YES, NO, or UNKNOWN.

        Question:
        {q}

        Patient answer:
        {a}

        Output:
        """
    out = llm(prompt)[0]["generated_text"].lower()
    if "yes" in out:
        return "yes"
    if "no" in out:
        return "no"
    return "unknown"


def smart_parse(q, a):
    r = parse_fast(a)
    if r != "unknown":
        return r, "fast"
    if len(str(a).split()) <= 2:
        return "unknown", "fast"
    r2 = llm_parse(q, a)
    return r2, "llm"


def select_flowchart_semantic(user_text):
    """Select the best-matching flowchart from user symptom description."""
    flowcharts = _load_flowcharts()
    index = _build_faiss_index()
    embedder = _load_embedder()
    import numpy as np
    q = embedder.encode([user_text])
    q = np.array(q).astype("float32")
    _, I = index.search(q, 1)
    return flowcharts[I[0][0]]


def show_result(fc, score):
    """Get triage result dict for a given score."""
    for t in fc["scoring"]["thresholds"]:
        if score >= t["min_score"]:
            return {
                "triage": t["triage"],
                "action": t["action"],
                "score": score,
            }
    return {"triage": "STANDARD", "action": "Clinic visit", "score": score}


def process_flowchart_step(fc, node_index, user_answer, trace=None):
    """
    Stateful flowchart processor. Process one Q&A step.
    Returns: (response_text, urgency_level, triage_result, next_question, updated_trace, session_state)
    """
    flowcharts = _load_flowcharts()
    nodes = list(fc["nodes"].items())
    if node_index >= len(nodes):
        return None, "STANDARD", None, None, trace, {}

    qid, node = nodes[node_index]
    question = node["question"]
    res, method = smart_parse(question, user_answer)

    if trace is None:
        trace = {
            "selected_flowchart": {
                "id": fc["id"],
                "title": fc["title"],
                "scenario": fc["scenario"],
            },
            "time": str(datetime.now()),
            "qa": [],
            "red_flag": None,
            "final": None,
        }

    step = {
        "qid": qid,
        "question": question,
        "answer": user_answer,
        "parsed_as": res,
        "parse_method": method,
        "score_delta": 0,
        "red_flag": False,
    }

    score_delta = 0
    red_flag_hit = False

    if res == "yes":
        score_delta = node["yes_score"]
        step["score_delta"] = score_delta
        if node.get("yes_red_flag"):
            step["red_flag"] = True
            red_flag_hit = True
    elif res == "no":
        score_delta = node["no_score"]
        step["score_delta"] = score_delta
        if node.get("no_red_flag"):
            step["red_flag"] = True
            red_flag_hit = True

    trace["qa"].append(step)
    current_score = sum(s["score_delta"] for s in trace["qa"])

    if red_flag_hit:
        trace["red_flag"] = step
        trace["final"] = show_result(fc, 999)
        urgency = trace["final"]["triage"]
        if urgency == "IMMEDIATE":
            urgency_level = "URGENT"
        else:
            urgency_level = urgency
        return (
            f"⚠️ Red flag detected. **Triage: {trace['final']['triage']}** - {trace['final']['action']}",
            urgency_level,
            trace["final"],
            None,
            trace,
            {"flowchart_id": fc["id"], "current_node_index": node_index + 1, "trace": trace, "completed": True},
        )

    next_node_index = node_index + 1
    if next_node_index >= len(nodes):
        trace["final"] = show_result(fc, current_score)
        final = trace["final"]
        urgency = final["triage"]
        if urgency == "IMMEDIATE":
            urgency_level = "URGENT"
        else:
            urgency_level = urgency
        return (
            f"**Triage: {final['triage']}** (Score: {current_score})\n\n**Action:** {final['action']}",
            urgency_level,
            final,
            None,
            trace,
            {"flowchart_id": fc["id"], "current_node_index": next_node_index, "trace": trace, "completed": True},
        )

    next_qid, next_node = nodes[next_node_index]
    next_question = next_node["question"]
    session_state = {
        "flowchart_id": fc["id"],
        "current_node_index": next_node_index,
        "trace": trace,
    }
    return (
        next_question,
        "NORMAL",
        None,
        next_question,
        trace,
        session_state,
    )


def generate_pdf(trace, filename=None):
    """Generate PDF report from trace. Returns file path."""
    import tempfile
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors

    if filename is None:
        fd, filename = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    el = []

    el.append(Paragraph("AI Triage Explainability Report", styles["Title"]))
    el.append(Spacer(1, 12))

    fc = trace["selected_flowchart"]
    f = trace["final"]

    el.append(Paragraph(f"<b>Flowchart:</b> {fc['title']} ({fc['scenario']})", styles["Normal"]))
    el.append(Paragraph(f"<b>Triage:</b> {f['triage']}", styles["Normal"]))
    el.append(Paragraph(f"<b>Action:</b> {f['action']}", styles["Normal"]))
    el.append(Paragraph(f"<b>Score:</b> {f['score']}", styles["Normal"]))
    el.append(Paragraph(f"<b>Time:</b> {trace['time']}", styles["Normal"]))
    el.append(Spacer(1, 12))

    data = [["QID", "Question", "User Answer", "Parsed", "Method", "Score"]]
    for q in trace["qa"]:
        data.append([
            q["qid"], q["question"], q["answer"],
            q["parsed_as"], q["parse_method"], str(q["score_delta"]),
        ])
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]))
    el.append(table)

    if trace.get("red_flag"):
        rf = trace["red_flag"]
        el.append(Spacer(1, 12))
        el.append(Paragraph("RED FLAG DETECTED", styles["Heading2"]))
        el.append(Paragraph(rf["question"], styles["Normal"]))
        el.append(Paragraph(rf["answer"], styles["Normal"]))

    doc.build(el)
    return filename


def ensure_models_loaded():
    """Pre-load all models (call at startup to avoid first-request latency)."""
    _load_flowcharts()
    _load_embedder()
    _build_faiss_index()
    # Optionally load LLM - can be slow
    # _load_llm()
