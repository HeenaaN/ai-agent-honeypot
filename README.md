# AI Agent Honeypot — MS Project
# AI Agent Honeypot — Detecting LLM-Powered Attackers

![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Ubuntu-orange)
![ML](https://img.shields.io/badge/ML-RandomForest%20F1%3D1.0-brightgreen)

> A novel cybersecurity research project that detects AI-powered attackers
> using prompt injection traps and machine learning classification.
> Built as part of an MS-level cybersecurity research project.

---

## What This Project Does

Modern attackers are using LLM-powered AI agents to automatically
attack servers. Current security tools (Snort, Suricata) cannot tell
the difference between a human attacker, a dumb bot, and an intelligent
AI agent. This project solves that problem.

**The system:**
1. Deploys a fake SSH server and web server (honeypot)
2. Hides prompt injection traps inside server responses
3. AI agents follow the traps — humans and bots ignore them
4. A machine learning classifier identifies the attacker type in real time

---

## Key Results

| Metric | Result |
|--------|--------|
| Random Forest F1 Score | 1.0 (100%) |
| XGBoost F1 Score | 0.97 (97%) |
| Classifier API Confidence | 98% |
| Trap Trigger Rate | 33.3% |
| Dataset Size | 150 labeled sessions |
| Attacker Classes | Human / Bot / AI Agent |

---

## System Architecture

```
Attacker
   |
   ├── SSH Attack ──► Cowrie Honeypot (port 2222)
   |                        |
   └── Web Attack ──► FastAPI Web Honeypot (port 8080)
                            |
                     Prompt Injection Traps
                     (50 traps across 5 surfaces)
                            |
                     Session Logger (JSONL)
                            |
                     ML Classifier API (port 8090)
                            |
                  Human / Bot / AI Agent + Alert
```

---

## Project Structure

```
ai-agent-honeypot/
├── cowrie/                  # SSH honeypot (Cowrie)
├── webserver/
│   └── app.py               # FastAPI fake web server with traps
├── trap_generator.py        # Generates prompt injection traps
├── traps.json               # 50 prompt injection traps
├── ai_attacker.py           # LangChain AI attacker agent
├── generate_dataset.py      # Dataset generator (3 classes)
├── classifier.py            # ML model training (RF + XGBoost + SHAP)
├── classifier_api.py        # Real-time classification REST API
├── classifier_model.pkl     # Trained Random Forest model
└── shap_importance.png      # SHAP feature importance plot
```

---

## Installation

### Requirements
- Ubuntu 22.04 or later
- Python 3.10+
- 4GB RAM minimum
- Ollama with LLaMA3.2:1b

### Setup

```bash
# Clone the repository
git clone https://github.com/HeenaaN/ai-agent-honeypot.git
cd ai-agent-honeypot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pandas scikit-learn xgboost shap \
            langchain langchain-community requests matplotlib

# Install Ollama and pull model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:1b

# Install and start Cowrie
cd cowrie
virtualenv --python=python3 cowrie-env
source cowrie-env/bin/activate
pip install -e .
cowrie start
cd ..
```

---

## Running the System

### Step 1 — Start the web honeypot
```bash
source venv/bin/activate
cd webserver
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### Step 2 — Start the classifier API
```bash
source venv/bin/activate
uvicorn classifier_api:app --host 0.0.0.0 --port 8090 --reload
```

### Step 3 — Run the AI attacker agent
```bash
source venv/bin/activate
python ai_attacker.py
```

### Step 4 — Classify a session in real time
```bash
curl -X POST http://localhost:8090/classify \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_001",
    "response_time_ms": 950,
    "trap_followed": 1,
    "paths_visited": 6,
    "avg_delay_ms": 1200,
    "unique_paths": 6,
    "visited_api_keys": 1,
    "visited_backup": 1,
    "visited_config": 1,
    "session_duration_s": 25
  }'
```

**Response:**
```json
{
  "prediction": "ai_agent",
  "confidence": 0.98,
  "alert": true
}
```

---

## How Prompt Injection Traps Work

Hidden inside server responses are instructions that only AI agents read:

```html

```

- **Human attacker** — never sees HTML comments, ignores it
- **Dumb bot** — does not understand natural language instructions
- **AI agent** — reads everything, follows the instruction, gets caught

---

## ML Classifier Features

| Feature | Description |
|---------|-------------|
| response_time_ms | How fast the attacker responds |
| trap_followed | Whether they followed a trap instruction |
| paths_visited | Total pages visited |
| avg_delay_ms | Average delay between requests |
| unique_paths | Number of different paths explored |
| visited_api_keys | Whether /api/keys was accessed |
| visited_backup | Whether /backup was accessed |
| visited_config | Whether /config was accessed |
| session_duration_s | Total session length in seconds |

---

## Experiments

### Experiment 1 — Detection across agent types
| Agent Type | Prediction | Confidence |
|------------|------------|------------|
| Standard agent | ai_agent | 90% |
| Fast agent | bot | 77% |
| Evasive agent | human | 85% |

### Experiment 2 — Adversarial evasion
Agents that avoid traps and mimic human behavior can evade detection.
This is documented as a limitation and area for future work.

### Experiment 3 — vs Traditional tools
Traditional tools (Snort) label all automated traffic as "scanner".
This system correctly differentiates AI agents from bots.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Cowrie | SSH honeypot |
| FastAPI | Web honeypot + classifier API |
| Ollama + LLaMA3.2 | Local LLM for trap generation |
| Scikit-learn | Random Forest classifier |
| XGBoost | Gradient boosted classifier |
| SHAP | Model explainability |
| LangChain | AI attacker agent |
| Docker | Container isolation |
| Ubuntu | Host operating system |

---

## Limitations

- Fast AI agents (sub-500ms) may be misclassified as bots
- Adversarial agents that avoid all traps can evade detection
- Dataset size is 150 sessions — larger dataset would improve accuracy
- Tested in isolated lab environment only

---

## Future Work

- Test against real-world AI agent frameworks (AutoGPT, BabyAGI)
- Deploy on public-facing server to collect real attack data
- Add LSTM sequence model for improved detection
- Implement real-time SIEM integration

---

## Author

**Heena** — MS Cybersecurity Research  
GitHub: [@HeenaaN](https://github.com/HeenaaN)

---

## License

MIT License — free to use for research and education.

---

## Acknowledgements

- [Cowrie Honeypot](https://github.com/cowrie/cowrie)
- [Palisade Research — AI Agent Honeypot Study 2025](https://www.palisaderesearch.org)
- [MITRE ATLAS Framework](https://atlas.mitre.org)
