# Real-Time Emergency Triage Orchestrator

> **AI-powered emergency triage assistant designed for low-bandwidth environments**
> Built for **WhatsApp-style interaction**, **2G compatibility**, and **rapid symptom escalation detection**.

---

## Problem Statement

In many real-world emergency situations, patients delay care even when symptoms are potentially life-threatening.

A classic example:

* **Chest pain delayed for 4 hours**
* No immediate triage
* No urgent action recommendation
* No accessible, low-tech health support system

This project aims to solve that gap.

### Core Goal

Design an AI system that can:

* **Assign WHO-style emergency urgency**
* **Detect dangerous red flags**
* **Ask follow-up triage questions**
* **Recommend immediate action**
* **Work in low-resource communication environments** such as:

  * WhatsApp
  * text-only chat
  * ≤ 50kb communication
  * 2G-compatible workflows

---

## Emergency Triage Objectives

The system must classify users into urgency categories such as:

* **IMMEDIATE**
* **VERY URGENT**
* **URGENT**
* **STANDARD**

And generate action plans like:

* **"Call 1122 NOW"**
* **"Go to the ER within 2 hours"**
* **"Seek urgent evaluation today"**
* **"Monitor and follow up if symptoms worsen"**

---

## Red Flag Detection Required

This project is specifically designed to catch **high-risk emergency presentations**.

### Examples:

* **Chest pain + radiation + diaphoresis**
  → Possible **Myocardial Infarction (MI)**

* **Sudden severe headache + neck stiffness**
  → Possible **Subarachnoid Hemorrhage (SAH)**

These are the types of patterns the system must never miss.

---

## Why We Rejected Black-Box Prediction Models

After going through multiple research papers, we realized one major issue:

> In healthcare triage, **accuracy alone is not enough**.
> The system must also explain **why** it made a decision.

That ruled out many standard ML prediction approaches for our use case.

### Why?

Because:

* The input is **text-based**, not image-based
* We need **interpretable triage reasoning**
* We need **safe question-by-question decision flow**
* A model saying *"urgent"* without a reason is not clinically trustworthy

### Why not standard XAI?

Most Explainable AI (XAI) approaches we explored were either:

* too image-focused
* too model-specific
* not suitable for dynamic conversational triage

So instead of building a pure prediction engine, we looked for something **safer, more explainable, and more clinically aligned**.

---

## Research Review

### Comparison of AI and Machine Learning Triage Research

We reviewed several relevant papers and compared their methods, datasets, strengths, and limitations.

| Title of Paper                                                                                 | Problem Being Solved                                                                         | Methodology                                                                                                           | Models Used                                                            | Model Comparison & Results                                                                                                     | Dataset Used                                                                          | Limitations                                                                                              |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Collaborative Medical Triage under Uncertainty: A Multi-Agent Dynamic Matching Approach**    | Poor specialization in AI triage, heterogeneous hospital structures, inefficient questioning | Multi-agent system (Recipient, Inquirer, Department agents) with dynamic matching guidance                            | DeepSeek-V3 (LLM)                                                      | 89.6% accuracy for primary department classification; 74.3% for secondary; guidance mechanisms significantly improved accuracy | 3,360 electronic health records from Ai Ai Yi Medical Network                         | Cross-specialty misclassification (Internal Medicine vs Surgery); diagnostic reasoning needs improvement |
| **C-PATH: Conversational Patient Assistance and Triage in Healthcare System**                  | Difficult healthcare navigation; hallucination and misinformation in LLMs                    | Multi-stage fine-tuning (Knowledge Injection, Instruction Tuning, Summarization) with conversation history management | LLaMA3-8B; BERT; ClinicalBERT                                          | Outperformed baselines; BERT achieved 0.996 accuracy on GPT-rewritten data vs 0.570 for ClinicalBERT                           | DDXPlus (5,000 cases) converted to conversations using GPT-3.5                        | Dataset bias toward respiratory diseases; hallucination and reasoning issues                             |
| **Multi-agent Self-Triage System with Medical Flowcharts (TriageMD)**                          | Lack of transparency in LLMs; non-urgent ED visits overload                                  | Multi-agent framework (Retrieval, Decision, Chat agents) guided by AMA flowcharts converted to graphs                 | GPT-4o-mini; FAISS                                                     | 95.29% accuracy for top-3 flowchart retrieval; 99.10% accuracy in flowchart navigation                                         | 100 AMA self-triage flowcharts; synthetic datasets (8,000 openings, 37,200 responses) | Only yes/no questions; weak error-handling for retrieval failures                                        |
| **Applications of AI and ML in Emergency Medicine Triage: A Systematic Review**                | ED overcrowding; low precision of traditional triage                                         | Systematic review (PRISMA); quality assessed with New Ottawa Scale                                                    | Decision trees, random forests, logistic regression, gradient boosting | ML models outperform conventional scores; gradient boosting slightly superior                                                  | 17 studies covering 14,180,371 participants                                           | Mostly observational; mixed pediatric and adult populations                                              |
| **AI Agents in Clinical Medicine: A Systematic Review**                                        | Unclear benefits of multi-agent systems vs single agents                                     | Systematic review of AI-agent-based clinical studies                                                                  | GPT-4 family, Llama-3, Claude-3 Opus, Gemini-1.5                       | All agent systems beat baseline LLMs; median improvement of 53 percentage points                                               | 20 studies using clinical cases, MCQs, patient data, genomics                         | High heterogeneity; reliance on synthetic data limits generalization                                     |
| **The Effects of Applying AI to Triage in the ED: A Systematic Review of Prospective Studies** | Need for faster and more accurate triage                                                     | Systematic review of prospective studies using STROBE                                                                 | Machine learning, fuzzy logic, feed-forward neural networks            | Accuracy ranged from 80.5%–99.1%; fuzzy clip model reached ~99% sensitivity/specificity                                        | 7 prospective studies from PubMed, CINAHL, etc.                                       | One neural network achieved only 33% precision for Level-1 triage                                        |
| **Multi-Agent AI Systems in Healthcare: Technical and Clinical Analysis (Concept Paper)**      | Scaling clinical operations; staffing shortages; endpoint optimization                       | Conceptual multi-agent architecture (7 agents) for complex care (e.g., sepsis)                                        | CNNs, Vision Transformers, RNNs, Reinforcement Learning                | Literature reports AI sepsis models outperform qSOFA and similar scores                                                        | Hypothetical system supported by literature review                                    | Mostly theoretical; lacks real-world validation                                                          |

---

## The Paper That Changed Our Direction

Among all the papers, **one stood out the most**.

It proposed a **flowchart-guided multi-agent triage system**, where:

* the patient query is analyzed first
* relevant medical flowcharts are retrieved
* the AI follows structured decision pathways
* the conversation becomes **safe, explainable, and clinically guided**

That was the turning point for our architecture.

---

## Reference Workflow

Below is the workflow inspiration that shaped our implementation:

<img width="1513" height="634" alt="image" src="https://github.com/user-attachments/assets/361ad13c-7256-4d2a-97f9-9a752e6ba48f" />

---

## Our Approach

### Hybrid Triage Reasoning System

Initially, we attempted a **hybrid AI + ML approach**.

#### Original idea:

* Build a **Knowledge Base (KB)** of medical triage logic
* Use an **LLM-powered chatbot** to interact with the patient
* Continuously ask **context-aware follow-up questions**
* Feed responses into traditional models such as:

  * Logistic Regression
  * Decision Trees
* Predict whether the patient was likely facing a serious condition

#### Why that failed

It still had a major issue:

> It could not provide enough **certainty**, **safety**, or **explainability** for emergency use.

Even if it predicted well, it was not reliable enough for real triage.

So we abandoned that direction and adopted the **flowchart-guided multi-agent reasoning system** inspired by the research paper.

That was the correct move.

---

## Final System Design

### Knowledge Base Construction

We created a **Flowchart Knowledge Base** covering 3 major medical complaint categories:

* **Chest-related issues**
* **Abdominal issues**
* **Diabetes-related issues**

#### Scope of the knowledge base:

* **10+ flowcharts for each problem area**
* **10–15 questions per graph**
* Included **combined-condition flowcharts** such as:

  * chest + abdominal symptoms together
  * overlapping symptom scenarios
  * escalating mixed symptom patterns

This gave us a more realistic triage structure instead of simplistic symptom matching.

---

## How the System Works

### High-Level Flow

#### Step 1 — User Input

The patient sends an initial symptom query.

Example:

* “I have chest pain and sweating”
* “Severe headache since morning”
* “My stomach hurts and I feel dizzy”

---

#### Step 2 — Flowchart Retrieval

The input is sent to **FAISS**, which retrieves the most relevant triage flowchart from the knowledge base.

#### Why FAISS?

Because it enables fast semantic retrieval of the most relevant medical pathway.

According to the referenced method:

* **Flowchart retrieval alone achieved 95%+ accuracy**

That makes it a strong first-stage triage router.

---

#### Step 3 — Chat Agent Follow-Up

Once the correct flowchart is retrieved:

* the **Chat Agent** asks the next medically relevant question
* the system avoids random LLM wandering
* every question stays anchored to structured triage logic

---

#### Step 4 — Answer Interpretation

After the patient responds:

* if the answer is simple (e.g. **yes/no**), it is directly used
* if the answer is free-text or ambiguous, an **Interpreter Agent** is used

This helps the system convert natural language into triage-compatible decision signals.

---

#### Step 5 — Decision Agent

Once the answer is interpreted:

* the **Decision Agent** decides:

  * the next question
  * whether a red flag is triggered
  * whether the case should be escalated
  * what urgency level should be assigned

---

#### Step 6 — Final Triage Recommendation

The system then produces:

* **Urgency level**
* **Immediate action recommendation**
* **Reasoning-aware response**

For example:

* “This may indicate a heart emergency. Call 1122 immediately.”
* “Your symptoms require urgent hospital assessment today.”
* “No immediate red flags detected, but you should monitor closely.”

---

## Architecture Summary

### Multi-Agent Pipeline

The full system behavior can be summarized as:

```text
User Query
   ↓
FAISS Flowchart Retrieval
   ↓
Chat Agent asks next triage question
   ↓
Interpreter Agent processes user response
   ↓
Decision Agent selects next node / urgency
   ↓
Final Action Plan + Risk Level
```

---

## Practical Implementation

This system was implemented using a **modular architecture**, where:

* **Backend intelligence** handles triage logic
* **Frontend interface** handles user interaction

This separation improves:

* maintainability
* scalability
* deployment flexibility
* debugging and testing

The two core files are:

* **`Untitled15.ipynb`** → Backend logic development
* **`app.py`** → Frontend user interface

---

## Backend Implementation – `Untitled15.ipynb`

`Untitled15.ipynb` was used to design and validate the **core triage decision logic**.

It contains:

* symptom parsing rules
* flowchart-based decision trees
* urgency classification logic
* response generation patterns

---

### How the Backend Was Implemented

1. The notebook was used for **rapid experimentation and testing**.
2. All triage logic was iteratively refined inside notebook cells.
3. Core decision functions were extracted from the notebook.
4. These functions were migrated into a backend service.
5. A **FastAPI backend** was built around them.
6. A `/diagnose` endpoint was created to expose the triage engine.
7. The API accepts:

   * patient symptoms
   * detected language
   * conversation history
8. The API returns:

   * medical response
   * urgency level
   * reasoning metadata

#### Result:

The notebook evolved from an experiment into a **production-ready backend service**.

---

## Frontend Implementation – `app.py`

`app.py` was built using **Streamlit** to create an interactive and accessible triage interface.

---

### Frontend Features

Implemented features include:

* **Chat-based interface**
* **Text input**
* **Voice input (speech-to-text)**
* **Automatic language detection**
* **Audio responses (text-to-speech)**
* **Session-based memory**
* **Emergency alert visualization**
* **Custom UI styling**

---

### How the Frontend Works

1. Streamlit components were structured into:

   * chat display
   * input form
   * voice controls
   * settings sidebar

2. Session state was used to:

   * store conversation history
   * prevent duplicate message processing

3. Language detection runs before every request.

4. Voice input is converted into text.

5. The user message is appended to session memory.

6. Data is sent to the backend using **HTTP POST**.

This gives the user a smooth, conversational triage experience while keeping all core decision-making in the backend.

---

## Running the Application

### Option 1 — Single Command (Recommended)

```bash
cd "Medical Triage System"
pip install -r requirements.txt
python app.py
```

#### What this does:

* Starts the **backend API** on port **8000**
* Starts the **Streamlit frontend** on port **7860**

Then open:

```text
http://localhost:7860
```

---

### Option 2 — Run Backend and Frontend Separately

#### Terminal 1 — Backend

```bash
cd "Medical Triage System"
pip install -r backend/requirements.txt
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 — Frontend

```bash
cd "Medical Triage System"
pip install -r frontend/requirements.txt
streamlit run frontend/app.py
```

Then open:

```text
http://localhost:8501
```

The frontend connects to the backend at:

```text
http://localhost:8000
```

by default.

---

## Deployment

### Hugging Face Spaces (Docker)

#### Steps

1. Create a new Space
2. Choose **Docker SDK**
3. Push this repository or upload the project files
4. Hugging Face will automatically build from the `Dockerfile`
5. Your app will go live

#### Demo URL format

```text
https://huggingface.co/spaces/<your-username>/<space-name>
```

---

### GitHub

GitHub should be used for:

* source code hosting
* collaboration
* version control
* documentation

#### Important Note

> **GitHub Pages cannot run this project**

Because this is a **Python/ML application**, not a static website.

For a live demo, use:

* **Hugging Face Spaces**
* or **Docker-based hosting**

---

## Project Structure

```bash
Medical Triage System/
├── backend/
│   ├── api.py                     # FastAPI with /diagnose endpoint
│   ├── triage_engine.py           # FAISS + TinyLlama triage logic
│   └── requirements.txt
├── frontend/
│   ├── app.py                     # Streamlit UI
│   └── requirements.txt
├── triage_flowcharts_weighted.json
├── app.py                         # Launcher (backend + frontend)
├── Dockerfile                     # For HF Spaces / Docker
├── .gitignore
└── README.md
```

---

## Why This Project Matters

Most triage systems fail in one of two ways:

### 1. They are too simplistic

They only classify symptoms into broad buckets and miss dangerous edge cases.

### 2. They are too black-box

They use models that cannot explain why a patient is being escalated.

This project takes a different path.

It combines:

* **structured medical reasoning**
* **retrieval-based safety**
* **multi-agent conversational flow**
* **real-world usability under poor connectivity**

That makes it far more practical for emergency-first healthcare support systems.

---

## Key Strengths

### What makes this system strong:

* **Explainable flowchart-guided reasoning**
* **Multi-agent decision architecture**
* **Low-bandwidth friendly**
* **Text-first design**
* **Emergency red flag prioritization**
* **Conversation-aware triage**
* **Modular deployment-ready architecture**

---

## Current Limitations

No serious README is complete without admitting what still needs work.

### Existing limitations include:

* Current knowledge base is limited to a few symptom domains
* Triage logic depends on quality of flowchart coverage
* Free-text interpretation may still require stronger medical NLP
* Some edge cases may require broader clinical validation
* Not yet clinically deployed or validated in hospital environments

---

## Future Improvements

Planned directions for improvement include:

* Expanding symptom coverage to more organ systems
* Adding multilingual medical triage support
* Improving ambiguous answer interpretation
* Integrating better emergency risk scoring
* Testing on real patient-like triage simulations
* Clinical validation with doctors / emergency specialists
* Better retrieval fallback handling
* More robust WhatsApp-native deployment workflows

---

## Final Note

This project is not trying to replace doctors.

It is trying to solve a much more immediate problem:

> **Helping people recognize danger sooner, ask the right questions faster, and act before it becomes too late.**

That is where triage matters most.

---

## Built For

* **AI Hackathons**
* **Healthcare AI research**
* **Emergency-first digital health systems**
* **Low-resource triage assistance**
* **Explainable AI in medicine**

---

## Credits

Developed as part of **AI Hackathon’26**
**All rights reserved**
