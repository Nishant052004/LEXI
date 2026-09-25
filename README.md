# 🤖 LEXI — Multi-Agent AI System & Intelligence OS

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.2+-black?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA--3.1--8B-f55036?style=flat)](https://groq.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS%204-38bdf8?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **LEXI** is an advanced, full-stack **Multi-Agent AI System** that coordinates specialized intelligent agents working in harmony to understand, process, and respond to user queries efficiently. Built with Generative AI, Retrieval-Augmented Generation (RAG), and Natural Language Processing (NLP), LEXI unites a cybernetic Next.js operating shell, a FastAPI telemetry backend, and high-speed Groq LPU inference into an extensible cognitive platform.

---

## 🌟 Why LEXI? The Multi-Agent Philosophy

Most AI chatbots try to make a single model do everything at once: parse intent, search the web, write code, recall past preferences, and generate a polite answer. When you overload a single prompt, hallucinations spike, latency suffers, and context gets lost.

**LEXI solves this with specialized, collaborative agents.** 

When you ask LEXI a question, an intelligent **Coordinator** activates an orchestration pipeline:
1. It dissects the emotional tone and linguistic nuances of your words (NLP).
2. It extracts key entities like people, organizations, dates, and emails (NER).
3. It searches your personalized memory bank to know who you are and what you care about (Memory).
4. If you need live facts, it browses the live web (Research).
5. If you need programming help, it enforces clean software architecture rules (Coding).
6. Finally, a synthesis engine fuses all this intelligence together through ultra-fast **Groq LPU hardware** (running LLaMA 3.1) to deliver an accurate, personalized response in milliseconds.

---

## 🤖 Meet the Agent Squad

```
                     ┌────────────────────────┐
                     │   User Input / Prompt  │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │   Coordinator Agent    │
                     │  (Pipeline Orchestrator)│
                     └───────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
 ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
 │   NLP Agent  │        │   NER Agent  │        │ Memory Agent │
 │ Intent, Tone │        │ Entities, PII│        │ History, DB  │
 └───────┬──────┘        └───────┬──────┘        └───────┬──────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │      Agent Router      │
                     │ (Dynamic Intent Map)   │
                     └───────────┬────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  ▼                             ▼
       ┌──────────────────────┐      ┌──────────────────────┐
       │    Research Agent    │      │     Coding Agent     │
       │  (DuckDuckGo Live)   │      │  (SOLID Principles)  │
       └──────────┬───────────┘      └──────────┬───────────┘
                  │                             │
                  └──────────────┬──────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │ Response Generation    │
                     │      Agent (Groq)      │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │   Synthesized Output   │
                     └────────────────────────┘
```

| Agent | Purpose | Powers |
|---|---|---|
| **🧠 Coordinator** | The central conductor | Manages context lifecycle, coordinates agent calls, tracks sub-millisecond execution telemetry, handles graceful fallbacks. |
| **💬 NLP Agent** | Understands how you speak | Uses NLTK VADER for sentiment, spaCy for lemmatization and tokenization, and regex-powered intent classification. |
| **🔍 NER Agent** | Remembers who and what | Extracts Persons, Organizations, Locations, Emails, and Phone Numbers. Supports dynamic custom entity patterns learned at runtime and saved to SQLite. |
| **🌐 Research Agent** | Eyes on the live web | Connects directly to DuckDuckGo to extract up-to-date web information without expensive search APIs. |
| **💻 Coding Agent** | Senior dev in your pocket | Injects production-ready code guidelines, enforces SOLID principles, clean formatting, and structured syntax. |
| **💾 Memory Agent** | Long-term personalized recall | Tracks conversation threads, stores user preferences, recognizes user patterns, and maintains interaction analytics. |
| **✨ Response Generation Agent** | The synthesizer | Combines agent outputs, developer instructions, and context into a polished response using Groq's high-speed inference. |

---

## 🖥️ Dual Frontends: Choose Your Workspace

LEXI includes two distinct interfaces built for different workflows:

### 1. 🚀 Next.js "AI OS" Shell (`/frontend`)
A futuristic, cybernetic web desktop interface built with **Next.js 16**, **Tailwind CSS 4**, and **Framer Motion**:
* **Command Center Dashboard**: Live telemetry, response latencies, active agents, and hardware health metrics.
* **Modern Chat View**: Streaming chat stream, markdown rendering, auto-scrolling, and thread switching.
* **Entity & Memory Explorer**: Inspect the entities and facts LEXI has learned about your topics.
* **Adaptive Theme System**: One-click toggling between deep cyber-dark mode and daylight clean mode.
* **Mobile-Responsive**: Tailored navigation bar, touch-friendly touch targets, and responsive viewports for phones and tablets.

### 2. 📊 Streamlit Intelligence Dashboard (`app.py`)
A fast dual-panel Python dashboard tailored for rapid testing, data inspection, and NLP analytics:
* Side-by-side prompt inspection and agent thought trace.
* Dynamic entity mapper: Add custom Named Entity Recognition patterns on the fly.
* Direct SQL conversation log inspection.

---

## 🛠️ Tech Stack & Architecture

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous, high-throughput REST API)
- **Inference Engine**: [Groq Cloud](https://groq.com/) with `llama-3.1-8b-instant`
- **NLP & Linguistics**: [spaCy](https://spacy.io/) (`en_core_web_sm`) & [NLTK](https://www.nltk.org/) (VADER sentiment, Punkt tokenizer)
- **Database & ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) with SQLite (fully Postgres-compatible)
- **Security**: JWT (`python-jose`) with bcrypt password hashing
- **Frontend OS**: [Next.js](https://nextjs.org/) 16, [React](https://react.dev/) 19, [Tailwind CSS](https://tailwindcss.com/) 4, [Lucide Icons](https://lucide.dev/)
- **Live Search**: `duckduckgo-search`

---

## ⚡ Quickstart Guide

Get LEXI running locally in under 5 minutes.

### 1. Clone the Repository
```bash
git clone https://github.com/Nishant052004/LEXI.git
cd LEXI
```

### 2. Configure Environment Variables
Copy the example environment template and populate your keys:
```bash
cp .env.example .env
```

Open `.env` in your editor and add your **Groq API Key**:
```env
# Get your free key at https://console.groq.com/keys
GROQ_API_KEY="gsk_your_actual_key_here"
LLM_MODEL="llama-3.1-8b-instant"
DATABASE_URL="sqlite:///./multi_agent_chatbot.db"
JWT_SECRET_KEY="create-a-random-secret-key"
```

### 3. Setup Python Backend
Create a virtual environment and install dependencies:
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Download required spaCy language model
python -m spacy download en_core_web_sm
```

### 4. Setup Next.js Frontend
```bash
cd frontend
npm install
cd ..
```

---

## 🚀 Running LEXI

You can launch the entire stack with a single command!

### Option A: One-Click Startup Script

**On Windows (PowerShell):**
```powershell
.\run_all.ps1
```

**On Linux / macOS (Bash):**
```bash
chmod +x start.sh
./start.sh
```

### Option B: Manual Service Startup

If you prefer launching each service in its own terminal:

1. **Start FastAPI Backend Server** (Port `8000`):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   * Interactive Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   * API Health Check: [http://localhost:8000/health](http://localhost:8000/health)

2. **Start Next.js AI OS Shell** (Port `3000`):
   ```bash
   cd frontend
   npm run dev
   ```
   * Open your browser at: [http://localhost:3000](http://localhost:3000)

3. **(Optional) Start Streamlit Analytics UI** (Port `8501`):
   ```bash
   streamlit run app.py --server.port 8501
   ```
   * Open your browser at: [http://localhost:8501](http://localhost:8501)

---

## 📡 API Reference Overview

The FastAPI backend exposes clean, structured endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user account |
| `POST` | `/api/auth/login` | Login and receive a JWT Bearer token |
| `POST` | `/api/chat/message` | Submit a prompt to the multi-agent pipeline |
| `GET` | `/api/history/{user_id}` | Retrieve past conversations and agent interactions |
| `GET` | `/api/entities/{convo_id}` | Get entities extracted from a specific thread |
| `POST` | `/api/entities/custom` | Dynamically register a new custom entity pattern |
| `GET` | `/api/profile/{user_id}` | Fetch user preferences and sentiment analytics |
| `GET` | `/api/monitoring/metrics` | Retrieve real-time execution metrics & latency stats |
| `GET` | `/health` | Server heartbeat and health status |

---

## 📁 Project Structure

```text
LEXI/
├── agents/                       # Specialized AI agent modules
│   ├── base_agent.py             # Abstract base agent class
│   ├── coding_agent.py           # Code generation & architecture agent
│   ├── memory_agent.py           # Context and memory retrieval agent
│   ├── ner_agent.py              # Named entity extraction agent
│   ├── nlp_agent.py              # Intent and sentiment agent
│   ├── research_agent.py         # DuckDuckGo web search agent
│   ├── response_generation_agent.py # Groq LLM synthesis agent
│   ├── registry.py               # Dynamic agent registry
│   └── router.py                 # Intent-to-agent router
├── api/                          # FastAPI route controllers
│   ├── auth.py                   # User registration and JWT authentication
│   ├── chat.py                   # Chat and pipeline execution endpoints
│   ├── entities.py               # Named entity endpoints & custom rules
│   ├── history.py                # Thread and conversation history
│   ├── profile.py                # User preference management
│   └── ops.py                    # Operations and system telemetry
├── config/                       # Central application configuration
│   └── config.py                 # Pydantic/Dotenv environment loader
├── database/                     # Database connection & session setup
│   └── connection.py             # SQLAlchemy engine and session factories
├── frontend/                     # Next.js 16 AI OS Shell
│   ├── src/app/                  # App Router, UI views, telemetry dashboard
│   ├── public/                   # Static assets & icons
│   └── package.json              # Frontend package definitions
├── memory/                       # Long-term memory management
│   └── memory_manager.py         # Conversation, entity, & interaction logger
├── models/                       # Data schemas and models
│   ├── db_models.py              # SQLAlchemy database tables
│   └── schemas.py                # Pydantic request/response schemas
├── ner/                          # Named Entity Recognition engine
│   └── ner_module.py             # spaCy + Regex + dynamic entity rules
├── nlp/                          # Natural Language Processing engine
│   └── nlp_module.py             # Tokenization, sentiment (VADER), intent
├── utils/                        # Logging, profiling, & metrics utilities
│   ├── logger.py                 # Structured application logger
│   └── metrics.py                # Sub-millisecond timing decorator
├── app.py                        # Streamlit interactive analytics dashboard
├── coordinator.py                # Core pipeline orchestration logic
├── llm.py                        # Direct Groq LLM helper
├── main.py                       # FastAPI application entrypoint
├── run_all.ps1                   # Single-click PowerShell launcher for Windows
├── start.sh                      # Single-click Bash launcher for Unix/Linux
├── requirements.txt              # Python production dependencies
└── .env.example                  # Environment configuration template
```

---

## 🧩 Extending LEXI: Add Your Own Agent in 3 Steps

LEXI was designed from day one to be easily extensible. You can plug in your own custom agents without modifying the core pipeline:

1. **Create your Agent Class** in `agents/my_agent.py`:
   ```python
   from agents.base_agent import BaseAgent

   class WeatherAgent(BaseAgent):
       @property
       def name(self) -> str:
           return "WeatherAgent"

       @property
       def description(self) -> str:
           return "Fetches live weather reports for specified cities."

       def execute(self, prompt: str, context: dict) -> dict:
           # Your custom logic here
           context["weather_data"] = "Sunny, 24°C"
           return {"status": "success", "agent": self.name}
   ```

2. **Register the Agent** in `agents/registry.py`:
   ```python
   from agents.my_agent import WeatherAgent
   agent_registry.register(WeatherAgent())
   ```

3. **Map the Intent** in `agents/router.py`:
   ```python
   agent_router.register_route("weather", "weatheragent")
   ```

That's it! LEXI's Coordinator will automatically route weather inquiries to your new agent.

---

## 🤝 Contributing

Contributions, feature suggestions, and pull requests are warmly welcomed!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Crafted with care by <a href="https://github.com/Nishant052004"><b>Nishant Rai</b></a>
</p>
