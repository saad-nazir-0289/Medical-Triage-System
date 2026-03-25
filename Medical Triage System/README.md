Case Study 2: Real-Time Emergency Triage
Orchestrator
The Problem: Delayed response to life-threatening symptoms (e.g., 4-hour delay for chest
pain).
Agent Challenges:
● Assign WHO Emergency Triage (IMMEDIATE / VERY URGENT / URGENT / STANDARD).
● Generate action plan: "Call 1122 NOW" vs. "Visit ER within 2 hours."
● Work via WhatsApp (text-only, ≤ 50kb, 2G compatible).
Red Flag Detection Required:
● Chest pain + radiation + diaphoresis → MI.
AI Hackathon’26. All rights reserved
● Sudden severe headache + neck stiffness → SAH.

## Our Approach in solving this problem:

After going through several Research papers we were sure that we can't use prediction model that doesn't explain why they did it what they did. since input is not going to be image based most XAI were also out. however we went through multiple approaches given below for references

## Comparison of AI and Machine Learning Triage Research

| Title of Paper | Problem Being Solved | Methodology | Models Used | Model Comparison & Results | Dataset Used | Limitations |
|---|---|---|---|---|---|---|
| **Collaborative Medical Triage under Uncertainty: A Multi-Agent Dynamic Matching Approach** | Poor specialization in AI triage, heterogeneous hospital structures, inefficient questioning | Multi-agent system (Recipient, Inquirer, Department agents) with dynamic matching guidance | DeepSeek-V3 (LLM) | 89.6% accuracy for primary department classification; 74.3% for secondary; guidance mechanisms significantly improved accuracy | 3,360 electronic health records from Ai Ai Yi Medical Network | Cross-specialty misclassification (Internal Medicine vs Surgery); diagnostic reasoning needs improvement |
| **C-PATH: Conversational Patient Assistance and Triage in Healthcare System** | Difficult healthcare navigation; hallucination and misinformation in LLMs | Multi-stage fine-tuning (Knowledge Injection, Instruction Tuning, Summarization) with conversation history management | LLaMA3-8B; BERT; ClinicalBERT | Outperformed baselines; BERT achieved 0.996 accuracy on GPT-rewritten data vs 0.570 for ClinicalBERT | DDXPlus (5,000 cases) converted to conversations using GPT-3.5 | Dataset bias toward respiratory diseases; hallucination and reasoning issues |
| **Multi-agent Self-Triage System with Medical Flowcharts (TriageMD)** | Lack of transparency in LLMs; non-urgent ED visits overload | Multi-agent framework (Retrieval, Decision, Chat agents) guided by AMA flowcharts converted to graphs | GPT-4o-mini; FAISS | 95.29% accuracy for top-3 flowchart retrieval; 99.10% accuracy in flowchart navigation | 100 AMA self-triage flowcharts; synthetic datasets (8,000 openings, 37,200 responses) | Only yes/no questions; weak error-handling for retrieval failures |
| **Applications of AI and ML in Emergency Medicine Triage: A Systematic Review** | ED overcrowding; low precision of traditional triage | Systematic review (PRISMA); quality assessed with New Ottawa Scale | Decision trees, random forests, logistic regression, gradient boosting | ML models outperform conventional scores; gradient boosting slightly superior | 17 studies covering 14,180,371 participants | Mostly observational; mixed pediatric and adult populations |
| **AI Agents in Clinical Medicine: A Systematic Review** | Unclear benefits of multi-agent systems vs single agents | Systematic review of AI-agent-based clinical studies | GPT-4 family, Llama-3, Claude-3 Opus, Gemini-1.5 | All agent systems beat baseline LLMs; median improvement of 53 percentage points | 20 studies using clinical cases, MCQs, patient data, genomics | High heterogeneity; reliance on synthetic data limits generalization |
| **The Effects of Applying AI to Triage in the ED: A Systematic Review of Prospective Studies** | Need for faster and more accurate triage | Systematic review of prospective studies using STROBE | Machine learning, fuzzy logic, feed-forward neural networks | Accuracy ranged from 80.5%–99.1%; fuzzy clip model reached ~99% sensitivity/specificity | 7 prospective studies from PubMed, CINAHL, etc. | One neural network achieved only 33% precision for Level-1 triage |
| **Multi-Agent AI Systems in Healthcare: Technical and Clinical Analysis (Concept Paper)** | Scaling clinical operations; staffing shortages; endpoint optimization | Conceptual multi-agent architecture (7 agents) for complex care (e.g., sepsis) | CNNs, Vision Transformers, RNNs, Reinforcement Learning | Literature reports AI sepsis models outperform qSOFA and similar scores | Hypothetical system supported by literature review | Mostly theoretical; lacks real-world validation |


among all the papers one stuck out to our eyes. It used the flowcharts to guide LLM's through the uer queries using multiple agents. The workflow is given below:

--

<img width="1513" height="634" alt="image" src="https://github.com/user-attachments/assets/361ad13c-7256-4d2a-97f9-9a752e6ba48f" />

## THEORETICAL IMPLEMENTATION

so we Tried to use the Hybrid Approach. in which we will take knowledge from knowledgeBase KB. A chatBot utilizing LLM's will communicate with the patient, and using the knowledge from that knowledge base, chatbot will keep asking users questions that are related to his problems. After those questions are answered, we will use multiple models such as Logistic Regeression or decision trees to predict whether the patient will have any problem or not. 
But the Problem was it couldn't predict with 100% certainity or accuracy. So we stuck using the approach this Paper shared. 

First we created a flowChart KnowledgeBase of 3 different scenerios such as Chest issues, Abdomimal Issues or diebetes issues that would recommend next question with more than 10+ flowcharts for each problem and 10-15 questions in each graph. Some FlowCharts were added for combined problems in these flowcharts like having chest and abdominal issues at the same time.

Working: User will input Query. Query will be received by FAISS that will look for the flowcharts related to it. it has 95%+ accuracy alone. After flowchart is retrived. the chat agent will ask question, after the ansewr is answered by user or patient, we will utilize it, first checking it with if fast answer can be supported like yes or no or if LLM is required to interpret that answer. after the interpreter agent interprets the answer, Then a decision agent will take action and choose the next question

## PRACTICAL IMPLEMENTATION

This system was implemented using a **modular architecture** where backend intelligence and frontend interaction are completely separated for scalability and maintainability.

The two core files are:

- **Untitled15.ipynb** → Backend logic development  
- **app.py** → Frontend user interface  

---

### Backend Implementation – `Untitled15.ipynb`

`Untitled15.ipynb` was used to design and validate the **core triage decision logic**. The notebook contains:

- Symptom parsing rules  
- Flowchart-based decision trees  
- Urgency classification logic  
- Response generation patterns  

#### How it was implemented:

1. The notebook was used for rapid experimentation and testing.
2. All decision logic was refined and validated inside notebook cells.
3. Core functions were extracted and migrated into a Python service.
4. A **FastAPI backend** was built around these functions.
5. An endpoint `/diagnose` was created to expose the logic.
6. The API accepts:
   - Patient symptoms
   - Detected language
   - Conversation history
7. The API returns:
   - Medical response
   - Urgency level
   - Reasoning metadata  

This converted the research notebook into a **production-ready backend service**.

---

### Frontend Implementation – `app.py`

`app.py` was built using **Streamlit** to provide an interactive user interface.

Features implemented:

- Chat-based interface  
- Text input  
- Voice input (speech-to-text)  
- Auto language detection  
- Audio responses (text-to-speech)  
- Session-based memory  
- Emergency alert visualization  
- Custom UI styling  

#### How it was implemented:

1. Streamlit components were structured into:
   - Chat display
   - Input form
   - Voice controls
   - Settings sidebar
2. Session state was used to:
   - Store conversation history
   - Prevent duplicate message processing
3. Language detection runs before every request.
4. Voice input is converted to text.
5. User message is appended to session memory.
6. Data is sent to backend using HTTP POST.

---

## Running the Application

### Option 1: Single Command (Recommended)
```bash
cd "Medical Triage System"
pip install -r requirements.txt
python app.py
```
This starts the backend API (port 8000) and Streamlit frontend (port 7860). Open http://localhost:7860

### Option 2: Separate Processes
**Terminal 1 – Backend:**
```bash
cd "Medical Triage System"
pip install -r backend/requirements.txt
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 – Frontend:**
```bash
cd "Medical Triage System"
pip install -r frontend/requirements.txt
streamlit run frontend/app.py
```
Then open http://localhost:8501 (or the URL Streamlit prints). The frontend connects to the backend at http://localhost:8000 by default.

---

## Deployment

### Hugging Face Spaces (Docker)
1. Create a new Space, choose **Docker** SDK.
2. Push this repository or upload the contents.
3. HF will build from the Dockerfile and run the app.
4. Live demo: `https://huggingface.co/spaces/<your-username>/<space-name>`

### GitHub
- Push the repo for code storage and version control.
- **Note:** GitHub Pages hosts static files only and cannot run this Python/ML app. Use Hugging Face Spaces for a live demo.

---

## Project Structure

```
Medical Triage System/
├── backend/
│   ├── api.py           # FastAPI with /diagnose endpoint
│   ├── triage_engine.py # FAISS + TinyLlama triage logic
│   └── requirements.txt
├── frontend/
│   ├── app.py           # Streamlit UI
│   └── requirements.txt
├── triage_flowcharts_weighted.json
├── app.py               # Launcher (backend + frontend)
├── Dockerfile           # For HF Spaces / Docker
├── .gitignore
└── README.md
```

