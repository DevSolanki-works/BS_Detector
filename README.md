# 🛡️ ContractGuard — The Local Legal BS Detector
### A College AI Project | Python + Streamlit + LangChain + Ollama

> **Privacy-first legal analysis. Every byte stays on your machine.**

---

## 📁 Project Architecture

```
ContractGuard/
│
├── app.py                          ← Main Streamlit UI (run this)
│
├── src/
│   ├── __init__.py
│   ├── llm_handler.py              ← LangChain + Ollama pipeline
│   ├── prompts.py                  ← All LLM system/user prompts
│   └── doc_parser.py              ← PDF / DOCX text extraction
│
├── sample_contracts/
│   └── rental_clause_sample.txt   ← Test contract for demos
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Local Setup (Step-by-Step)

### Step 1 — Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows → Download from https://ollama.com/download
```

### Step 2 — Pull a local model (pick one)

```bash
ollama pull llama3:8b       # Recommended — best balance
ollama pull mistral:7b      # Faster on lower-RAM machines
ollama pull phi3:mini       # Lightest — works on 8GB RAM laptops
```

### Step 3 — Start the Ollama server

```bash
ollama serve
# Keep this terminal open. Ollama listens on http://localhost:11434
```

### Step 4 — Clone / set up the Python project

```bash
# Create and activate a virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 5 — Run the app

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 🎓 Showing it to Your Professors

### Option A — Run on Your Laptop (Best for classroom demos)
This is the default setup. Just run both `ollama serve` and `streamlit run app.py`
and show the browser. Emphasise that the network tab shows ZERO external requests.

### Option B — Share on Your Local Network (Lab demo)
```bash
# Find your IP
hostname -I   # Linux/macOS
ipconfig      # Windows

# Run Streamlit accessible on local network
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
Professors on the same WiFi can open: `http://<your-ip>:8501`

### Option C — Deploy to Streamlit Community Cloud (Online demo link)
1. Push your code to a **public GitHub repo**
2. Sign up at https://streamlit.io/cloud
3. Connect your repo and set the main file to `app.py`
4. ⚠️ Note: Cloud deployment uses the Anthropic API instead of Ollama —
   update `llm_handler.py` to use `langchain_anthropic.ChatAnthropic`

---

## 🧩 Key Design Decisions (For Your Viva)

| Decision | Reason |
|---|---|
| **Ollama** over OpenAI | 100% local, no API cost, no data privacy concern |
| **LangChain** | Standardised pipeline; swap models with 1 line of code |
| **Streamlit** | Fastest way to build a Python ML web UI; no HTML/JS needed |
| **JSON output enforced** | Structured LLM output = reliable parsing, better UX |
| **Modular src/ layout** | Separation of concerns; each file has one job |
| **Temperature = 0.1** | Low randomness = consistent JSON, fewer parse errors |
| **pdfplumber** over PyPDF | Better text extraction from complex Indian contract PDFs |

---

## 🔬 How the LLM Pipeline Works

```
User pastes text
      │
      ▼
doc_parser.py  (extract if PDF/DOCX)
      │
      ▼
prompts.py     (inject text into system + user prompt template)
      │
      ▼
llm_handler.py (send to Ollama via LangChain → get raw JSON string)
      │
      ▼
parse_llm_output() (strip fences → parse JSON → dict)
      │
      ▼
app.py         (render 4-section dashboard in Streamlit)
```

---

## 📦 Library Reference

| Library | Role |
|---|---|
| `streamlit` | Web UI framework |
| `langchain` | LLM orchestration & prompt templating |
| `langchain-ollama` | LangChain adapter for Ollama models |
| `ollama` | Python client for local Ollama server |
| `pdfplumber` | PDF text extraction |
| `python-docx` | DOCX text extraction |
| `pydantic` | Data validation (used internally by LangChain) |
| `python-dotenv` | Load env vars from .env file (optional) |

---

## 🛠️ Troubleshooting

**"Connection refused" error**
→ Run `ollama serve` in a separate terminal first.

**"Model not found" error**
→ Run `ollama pull llama3:8b` (or whichever model you selected).

**JSON parse error from LLM**
→ Lower the temperature slider to 0.0, or switch to a larger model.

**Slow analysis (>2 minutes)**
→ Use `phi3:mini` or `mistral:7b`. Llama 3 70B needs 32GB+ RAM.

**ImportError on startup**
→ Make sure your virtual environment is activated before running pip install.

---

*Built as a college project demonstrating local, private AI for legal document analysis.*
*Not a substitute for professional legal advice.*
