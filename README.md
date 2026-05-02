# MAS Code Review Pipeline 🤖
### SE4010 – CTSE Assignment 2 | SLIIT | 2026

A locally-hosted **Multi-Agent System (MAS)** that automates Python code review using LangGraph, Ollama (llama3:8b), and FastAPI. Four specialized AI agents work together to understand, analyze, fix, and test your Python code — entirely offline with zero cloud costs.

---

## 🎯 What It Does

Upload any Python file and the system will:

1. 🔵 **Understand** — Reads and summarizes the code structure
2. 🔴 **Analyze** — Finds bugs, code smells, and security vulnerabilities
3. 🟡 **Fix** — Generates a corrected version with inline comments
4. 🟢 **Test** — Writes and runs pytest unit tests on the fixed code
5. 📄 **Report** — Produces a full markdown report of all findings

---

## 🤖 Agent Pipeline

```
[Python File]
     │
     ▼
CodeUnderstandingAgent  →  Understands code purpose & structure
     │
     ▼
BugAnalystAgent         →  Finds bugs, smells & security issues
     │
     ▼
FixGenerationAgent      →  Generates fixed code with # FIX: comments
     │
     ▼
TestValidationAgent     →  Generates & runs pytest tests
     │
     ▼
[Report + Fixed Code]
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM Engine | Ollama + llama3:8b (local) |
| Orchestration | LangGraph |
| LLM Interface | langchain-ollama |
| Linting | flake8 |
| Security Scanning | bandit |
| Testing | pytest |
| Backend API | FastAPI + uvicorn |
| Frontend | React + Vite |

---

## 📦 Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com/download) installed

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd mas-code-review
```

### 2. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install langchain-community langgraph langchain-core langchain-ollama flake8 bandit pytest fastapi uvicorn python-multipart pytest-cov
```

### 4. Pull the LLM Model
```bash
ollama pull llama3:8b
```

### 5. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## ▶️ Running the System

You need **3 terminals** running simultaneously:

### Terminal 1 — Ollama (LLM Server)
```bash
ollama serve
```
> Ollama auto-starts on Windows after installation

### Terminal 2 — Backend API
```bash
# Activate venv first
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

uvicorn api:app --reload --port 8000
```

### Terminal 3 — Frontend
```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser 🎉

---

## 💻 CLI Usage

You can also run the pipeline from the command line:

```bash
python main.py path/to/your/file.py
```

**Example:**
```bash
python main.py tests/sample_inputs/buggy_code.py
```

**Example Output:**
```
==================================================
   MAS Code Review Pipeline
   Powered by LangGraph + llama3:8b
==================================================
📂 Analyzing: tests/sample_inputs/buggy_code.py
🚀 Starting pipeline...

✅ Status         : completed
📝 Functions      : 9 found
🔢 Complexity     : 7
🐛 Bugs Found     : 16
🔐 Security Issues: 7
✨ Fixes Applied  : 10
🧪 Tests Passed   : 14
❌ Tests Failed   : 5
📄 Report Saved   : outputs/report_20260423_151318.md
==================================================
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run individual student tests
pytest tests/test_code_understanding.py -v   # Student 1
pytest tests/test_bug_analyst.py -v          # Student 2
pytest tests/test_fix_generation.py -v       # Student 3
pytest tests/test_validation_agent.py -v     # Student 4

# Run with coverage report
pytest tests/ --cov=agents --cov=tools
```

**Test Results:**
```
50 passed in 129.63s ✅
```

---

## 📁 Project Structure

```
mas-code-review/
├── agents/
│   ├── code_understanding_agent.py   # Agent 1
│   ├── bug_analyst_agent.py          # Agent 2
│   ├── fix_generation_agent.py       # Agent 3
│   └── test_validation_agent.py      # Agent 4
├── tools/
│   ├── read_and_parse_code.py        # Tool 1 (Student 1)
│   ├── run_linter_and_scanner.py     # Tool 2 (Student 2)
│   ├── save_fixed_code.py            # Tool 3 (Student 3)
│   └── run_tests.py                  # Tool 4 (Student 4)
├── state/
│   └── agent_state.py                # Global state TypedDict
├── graph/
│   └── pipeline.py                   # LangGraph pipeline
├── tests/
│   ├── conftest.py                   # Shared fixtures
│   ├── test_code_understanding.py    # 14 tests
│   ├── test_bug_analyst.py           # 12 tests
│   ├── test_fix_generation.py        # 12 tests
│   └── test_validation_agent.py      # 12 tests
├── utils/
│   └── logger.py                     # JSON structured logging
├── logs/                             # Execution logs (auto-generated)
├── outputs/                          # Fixed code & reports (auto-generated)
├── frontend/                         # React + Vite UI
├── api.py                            # FastAPI backend
├── main.py                           # CLI entry point
└── requirements.txt
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check if API is running |
| POST | `/analyze` | Upload .py file for analysis |

**Health Check:**
```bash
curl http://localhost:8000/health
# {"status": "ok", "model": "llama3:8b"}
```

**Analyze File:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@your_code.py"
```

---

## 📊 Sample Results on Buggy Code

Running the pipeline on `tests/sample_inputs/buggy_code.py`:

| Metric | Result |
|---|---|
| Functions Detected | 9 |
| Complexity Score | 7 |
| Bugs Found | 16 |
| Security Issues | 7 |
| Fixes Applied | 10 |
| Tests Generated | 70 lines |
| Tests Passed | 14 |
| Execution Time | ~90 seconds |

---

## 📋 Output Files

After running the pipeline, check the `outputs/` folder:

| File | Description |
|---|---|
| `fixed_<timestamp>_<name>.py` | Corrected Python file |
| `report_<timestamp>.md` | Full markdown analysis report |

Logs are saved to `logs/run_<timestamp>.log` in JSON Lines format.

---

## 👥 Team Members

| Student | Agent | Tool |
|---|---|---|
| [Student 1 Name] | CodeUnderstandingAgent | read_and_parse_code |
| [Student 2 Name] | BugAnalystAgent | run_linter_and_scanner |
| [Student 3 Name] | FixGenerationAgent | save_fixed_code |
| [Student 4 Name] | TestValidationAgent | run_tests |

---

## ⚠️ Important Notes

- This system runs **100% locally** — no internet required after setup
- Paid APIs (OpenAI, Anthropic) are **not used**
- Processing time depends on your hardware (~30-90 seconds per file)
- Larger files with more functions will take longer to process

---

## 📄 License

This project was developed for educational purposes as part of SE4010 – CTSE at SLIIT.
