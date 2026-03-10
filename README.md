# 🔬 AI Research Assistant — Multi-Agent System

A production-ready multi-agent AI research pipeline built with **CrewAI**, **Google Gemini 2.0 Flash**, and **Streamlit**. Five specialized AI agents collaborate autonomously to take any research topic and produce a comprehensive, cited research report.

---

## 🤖 Agent Architecture

```
User Topic
    │
    ▼
┌─────────────┐
│  🗺️ Planner  │  Breaks topic into 3–7 focused sub-questions
└──────┬──────┘
       │
    ▼
┌──────────────┐
│ 🔍 Researcher │  Searches the web for each sub-question (Tavily API)
└──────┬───────┘
       │
    ▼
┌───────────────┐
│ 📝 Summarizer  │  Distills findings into structured insights
└──────┬────────┘
       │
    ▼
┌──────────────┐
│  🧐 Critic   │  Reviews quality, scores /10, flags gaps
└──────┬───────┘
       │
    ▼
┌─────────────┐
│  ✍️ Writer   │  Writes polished final report addressing critic feedback
└─────────────┘
       │
    ▼
📄 Markdown Report + PDF Export
```

The **Critic → Writer feedback loop** is what makes this system production-grade — the Writer must address all quality issues raised by the Critic before delivering the final output.

---

## ✨ Features

- **5 specialized agents** with distinct roles, goals, and backstories
- **Critic feedback loop** — Writer receives quality score and must address gaps
- **Configurable depth** — Quick (3 questions) / Standard (5) / Deep (7)
- **Live agent status** — real-time pipeline visualization in the UI
- **PDF export** — styled, downloadable research reports
- **Source attribution** — all claims linked back to web sources
- **Per-agent outputs** — view each agent's work in dedicated tabs

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | [CrewAI](https://crewai.com) |
| LLM | Google Gemini 2.0 Flash |
| Web Search | [Tavily API](https://tavily.com) |
| UI | Streamlit |
| PDF Export | ReportLab |
| LLM Integration | LangChain Google GenAI |

---

## 🚀 Getting Started

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd research-agent
pip install -r requirements.txt
```

### 2. Get API Keys

| API | Where | Cost |
|-----|-------|------|
| Google Gemini | [aistudio.google.com](https://aistudio.google.com) | Free |
| Tavily Search | [tavily.com](https://tavily.com) | Free (1000/mo) |

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your keys
```

```env
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 4. Run

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 📁 Project Structure

```
research-agent/
├── agents/
│   ├── __init__.py
│   ├── planner.py       # Research Planner Agent
│   ├── researcher.py    # Web Researcher Agent
│   ├── summarizer.py    # Summarizer Agent
│   ├── critic.py        # Critic Agent
│   └── writer.py        # Report Writer Agent
├── tools/
│   ├── __init__.py
│   ├── search_tool.py   # Tavily web search tool
│   └── pdf_export.py    # ReportLab PDF generator
├── app.py               # Streamlit UI
├── pipeline.py          # Agent orchestration (CrewAI)
├── requirements.txt
├── .env.example
└── README.md
```

---

## 💡 Example Topics

- "The impact of large language models on software engineering jobs"
- "Quantum computing progress in 2025"
- "AI regulation in the European Union"
- "CRISPR gene editing recent advances"
- "The future of nuclear energy"

---

## 📄 License

MIT
