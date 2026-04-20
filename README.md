# 🛡️ ContractGuard — The Legal BS Detector
### Applied AI Mini Project | April 2026

> Paste any contract, lease, or terms of service → get a plain-English breakdown, red flags, and Hindi & Gujarati translations in under 10 seconds.

**Live URL:** https://bsdetector-tzxf2yrje4apphyzndjrlkb.streamlit.app

---

## 📁 Project Structure

```
BS_Detector/
│
├── app.py                        ← Main Streamlit app (run this)
├── Dockerfile                    ← Docker container config
├── generate_and_train.py         ← Generates synthetic data + trains Phase 2 model
├── requirements.txt              ← Python dependencies
│
├── src/
│   ├── __init__.py
│   ├── llm_handler.py            ← Groq API + LangChain pipeline
│   ├── prompts.py                ← System prompts for the LLM
│   ├── doc_parser.py             ← PDF / DOCX text extraction
│   └── classifier.py            ← Teachable Machine document classifier
│
├── model/
│   ├── keras_model.h5            ← Trained TensorFlow model (Phase 2)
│   └── labels.txt                ← Class names for classifier
│
├── sample_contracts/
│   └── rental_clause_sample.txt  ← Demo contract for testing
│
└── synthetic_data/               ← Auto-generated training images
```

---

## 🚀 Three Ways to Run

### Option 1 — Normal Python (simplest)

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```
Open http://localhost:8501

---

### Option 2 — Docker (what we used)

Docker packages everything into a container so it runs identically on any machine — no "works on my machine" problems.

```powershell
# Step 1: Build the Docker image (only needed once, or when you change code)
docker build -t contractguard .

# Step 2: Run the container
docker run -p 8501:8501 contractguard
```
Open http://localhost:8501

**Other useful Docker commands:**
```powershell
# Run with your Groq API key passed in
docker run -p 8501:8501 -e GROQ_API_KEY=gsk_yourkey contractguard

# Stop all running containers
docker stop $(docker ps -q)

# See all your built images
docker images

# Remove the image to rebuild fresh
docker rmi contractguard
```

**What the Dockerfile does (line by line):**
```dockerfile
FROM python:3.12-slim          # Start from a clean Python 3.12 Linux environment
WORKDIR /app                   # Set working directory inside container
RUN pip install --upgrade pip  # Upgrade pip first
COPY requirements.txt .        # Copy only requirements first (for Docker cache)
RUN pip install -r requirements.txt  # Install all dependencies
COPY . .                       # Copy all project files into container
EXPOSE 8501                    # Tell Docker the app uses port 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

### Option 3 — Streamlit Cloud (live public URL)

1. Push code to GitHub
2. Go to share.streamlit.io → connect repo → deploy
3. Settings → Secrets → add: `GROQ_API_KEY = "gsk_your_key"`
4. Get a public URL to share with anyone

---

## 🤖 Phase 2 — Train the Document Classifier

```powershell
# Install TensorFlow (one time)
pip install tensorflow Pillow numpy

# Generate 320 synthetic images + train the model (~5 mins)
python generate_and_train.py
```

This creates `model/keras_model.h5` and `model/labels.txt` automatically. The model classifies uploaded document images into 4 categories: Rental Agreement, Employment Contract, Terms of Service, Other.

---

## 🔑 API Key Setup

Get a free Groq API key (no credit card) at **console.groq.com**

**Local:** Enter in the sidebar text field when running the app.

**Docker:** `docker run -p 8501:8501 -e GROQ_API_KEY=gsk_yourkey contractguard`

**Streamlit Cloud:** Manage App → Settings → Secrets → paste `GROQ_API_KEY = "gsk_..."`

---

## 📦 Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| UI | Streamlit | Web interface |
| LLM | Groq API + Llama 3.1 8B | Contract analysis |
| Orchestration | LangChain | Prompt + model pipeline |
| Phase 2 Model | Teachable Machine / TensorFlow | Document image classifier |
| Document Parsing | pdfplumber + python-docx | Read PDF and Word files |
| Deployment | Streamlit Cloud + Docker | Hosting |

---

## ⚠️ Disclaimer

ContractGuard is an educational AI tool. It is not a substitute for professional legal advice. Always consult a qualified lawyer before signing important contracts.
