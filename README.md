# ☕ Starbucks AI Operations Intelligence System

> A portfolio-grade AI Engineering project built on 100,000 Starbucks transactions.
> Demonstrates: ML models, REST APIs, LLM integration, and interactive dashboards.

---

## 🗺️ Project Map

```
starbucks_ai/
├── data/
│   └── starbucks_customer_ordering_patterns.csv   ← PUT YOUR CSV HERE
│
├── models/                                         ← Auto-created when you run Phase 1
│   ├── spend_prediction_model.pkl
│   ├── wait_time_model.pkl
│   ├── kmeans_model.pkl
│   ├── label_encoders.pkl
│   └── cluster_scaler.pkl
│
├── phase1_ml_models.py      ← Data analysis + ML training
├── phase2_fastapi.py        ← REST API server
├── phase3_llm_analyst.py    ← Natural language Q&A
├── phase4_dashboard.py      ← Streamlit web dashboard
├── requirements.txt         ← All dependencies
└── .env                     ← Your API key (create this yourself)
```

---

## 🚀 Setup (Do This First — One Time Only)

### Step 1: Put the CSV in the right place
```
Copy your CSV file to:  starbucks_ai/data/starbucks_customer_ordering_patterns.csv
```

### Step 2: Create a virtual environment (keeps your project isolated)
```bash
# In your terminal, navigate to the starbucks_ai folder first
cd starbucks_ai

# Create virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# You'll see (venv) appear in your terminal prompt — that means it worked!
```

### Step 3: Install all dependencies
```bash
pip install -r requirements.txt
```
This installs everything: pandas, scikit-learn, fastapi, streamlit, anthropic, etc.

### Step 4: Create your .env file (for API key)
```bash
# Create a file called .env in the starbucks_ai folder
# Add this line (replace with your actual key):
ANTHROPIC_API_KEY=sk-ant-your-key-here
```
Get a free key at: https://console.anthropic.com

---

## 📋 Running Each Phase

### Phase 1: Train the ML Models
```bash
python phase1_ml_models.py
```
**What it does:** Loads data, trains 3 models, saves them to the models/ folder.
**Takes:** ~2 minutes
**Output:** See models/ folder fill up with .pkl files + charts

---

### Phase 2: Start the API Server
```bash
python phase2_fastapi.py
```
**What it does:** Starts a web server on your computer at http://localhost:8000
**Interactive docs:** Open http://localhost:8000/docs in your browser
   → You can test every endpoint by clicking buttons — no code needed!

**Why this matters for your CV:**
You've now turned your ML models into a DEPLOYABLE SERVICE.
Any app, website, or mobile app could now call your predictions.

**Leave this running** while you use the dashboard.

---

### Phase 3: Ask Questions in Plain English
```bash
python phase3_llm_analyst.py
```
**What it does:** Lets you have a conversation with your data.
**Example questions:**
- "Which ordering channel has the worst wait times?"
- "Why do older customers avoid the mobile app?"
- "What should we do to increase mobile adoption in rural stores?"

---

### Phase 4: Open the Dashboard
```bash
streamlit run phase4_dashboard.py
```
**What it does:** Opens a beautiful web dashboard at http://localhost:8501

**Features:**
- 📊 Overview: KPIs, charts, trends
- 🔮 Predictions: Enter any customer profile and get AI predictions
- 👥 Segments: Customer persona cards
- 🤖 AI Analyst: Chat interface powered by Claude

---

## 🎓 What You Learned (What to Say in Interviews)

### "What does Phase 1 teach you?"
> "I learned how to do EDA (Exploratory Data Analysis) with pandas, encode categorical
> features for ML models, train Random Forest regressors for prediction tasks, and use
> K-Means clustering for unsupervised customer segmentation. I evaluated models using
> MAE and R² metrics."

### "What does Phase 2 teach you?"
> "FastAPI is a Python framework for building REST APIs. An API (Application Programming
> Interface) is how two programs talk to each other over the internet. I wrapped my ML
> models in HTTP endpoints using POST requests, defined data validation schemas with
> Pydantic, and learned the difference between GET and POST requests."

### "What does Phase 3 teach you?"
> "I used the Anthropic API to add a natural language layer on top of structured data.
> The key technique is RAG-adjacent: I pre-compute statistics from the dataset and inject
> them into the LLM's context window, so it gives accurate data-grounded answers instead
> of hallucinating."

### "What does Phase 4 teach you?"
> "Streamlit is a Python library that converts scripts into interactive web apps. I used
> session_state for chat history persistence, Plotly for interactive charts, and connected
> the frontend to my FastAPI backend. This creates a complete full-stack application."

---

## 🐳 Bonus: Docker (When You're Ready)

Docker packages your app so it runs identically on ANY computer.
Think of it as a shipping container for your code.

```dockerfile
# Dockerfile (create this in your starbucks_ai folder)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "phase2_fastapi.py"]
```

```bash
# Build the container
docker build -t starbucks-ai .

# Run it
docker run -p 8000:8000 starbucks-ai
```

**Why this matters:** Your API now runs in an isolated container.
It works on Windows, Mac, Linux, and cloud servers — guaranteed.

---

## 📝 CV Description

**Starbucks AI Operations Intelligence System**
*Python · FastAPI · Scikit-learn · Streamlit · Anthropic API · Docker*

Built an end-to-end ML pipeline analyzing 100K Starbucks transactions to predict
customer spend and order fulfillment time (MAE: $X, R²: 0.XX). Deployed 3 ML models
(Random Forest, K-Means) as a RESTful API using FastAPI and Docker. Integrated
Claude (Anthropic LLM) to enable natural language querying of operational data.
Visualized insights in a Streamlit dashboard featuring real-time predictions and
AI-powered customer segment analysis.
