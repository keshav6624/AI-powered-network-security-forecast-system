## NetGuard AI — Network Attack Forecasting

AI-powered network security system that forecasts the probability of a future network attack using temporal network behaviour, machine learning, and deep learning.

Built for **SIH26153** using the **CSE-CIC-IDS2018** dataset.

## Features

- Forecasts future attacks instead of only detecting current traffic
- LSTM and Transformer-based temporal forecasting
- Logistic Regression and XGBoost baselines
- Isolation Forest for anomaly detection
- Risk score from 0–100
- LOW / MEDIUM / HIGH / CRITICAL risk levels
- Early warning alerts
- Historical network traffic replay
- SOC-style security dashboard
- Model comparison
- PostgreSQL with SQLite fallback
- Demo mode without trained models
- Docker support

---

## Architecture

```text
CSE-CIC-IDS2018
        │
        ▼
Network Flow Windows
        │
        ▼
Feature Preprocessing
        │
        ├── Logistic Regression
        ├── XGBoost
        ├── LSTM
        ├── Transformer
        └── Isolation Forest
                │
                ▼
        Prediction Ensemble
                │
                ▼
          Risk Engine
                │
          ┌─────┴─────┐
          ▼           ▼
       Alerts      SOC Dashboard
````

### Forecasting Flow

```text
Historical Network Behaviour
            │
            ▼
     [t-9 ... t] Sequence
            │
            ▼
    LSTM / Transformer
            │
            ▼
    Attack Probability
            │
            ▼
       Future t + 5m
            │
            ▼
      Risk Score 0–100
            │
            ▼
       Early Warning
```

---

## Project Structure

```text
NetGuard-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── ml/
│   │   ├── services/
│   │   ├── database/
│   │   ├── schemas/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
│
├── models/
│   ├── baseline/
│   ├── xgboost/
│   ├── lstm/
│   ├── transformer/
│   ├── isolation_forest/
│   └── preprocessing/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── experiments/
├── docs/
├── docker-compose.yml
└── README.md
```

---

## How It Works

NetGuard AI analyses a sequence of recent network states and predicts the probability of an attack occurring in the next 5 minutes.

Example:

```text
10:00  Normal
10:01  Normal
10:02  Suspicious
10:03  Suspicious
10:04  Suspicious
          │
          ▼
10:05  Attack Probability: 91%
       Risk Score: 87
       Severity: CRITICAL
```

This allows security teams to receive an early warning before the predicted attack window.

---

## Models

| Model               | Purpose              |
| ------------------- | -------------------- |
| Logistic Regression | Baseline model       |
| XGBoost             | Tabular benchmark    |
| LSTM                | Temporal forecasting |
| Transformer         | Temporal forecasting |
| Isolation Forest    | Anomaly detection    |

The LSTM and Transformer analyse historical sequences to forecast future attack probability.

Isolation Forest provides an additional anomaly signal and is not used as a forecasting model.
---

## Model Accuracy
Logistic Regression — 99.69%
Isolation Forest — 99.27%
LSTM — 98.33%
Temporal Transformer — 96.14%
Retrained XGBoost — 66.67%
---

## Risk Levels

| Risk Score | Level    |
| ---------: | -------- |
|       0–30 | LOW      |
|      31–60 | MEDIUM   |
|      61–80 | HIGH     |
|     81–100 | CRITICAL |

High-risk predictions can generate alerts that appear on the SOC dashboard.

---

## Tech Stack

**Backend:** FastAPI, Python, SQLAlchemy

**Frontend:** React, Vite, Tailwind CSS, Recharts, React Flow

**Machine Learning:** Scikit-learn, XGBoost, PyTorch, TensorFlow/Keras

**Database:** PostgreSQL / SQLite

**Deployment:** Docker

**Dataset:** CSE-CIC-IDS2018

---

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

### Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

## Docker

Run the complete application:

```bash
docker compose up --build
```

Services:

```text
Frontend  → http://localhost
Backend   → http://localhost:8000
Swagger   → http://localhost:8000/docs
PostgreSQL → localhost:5432
```

---

## Demo Mode

NetGuard AI supports running without trained model artifacts.

Set:

```env
DEMO_MODE=true
```

Demo mode uses deterministic mock predictions and allows the complete dashboard and replay system to run without trained models.

After installing the trained models:

```env
DEMO_MODE=false
```

The application automatically loads the available artifacts from:

```text
models/
```

No application code changes are required.

---

## API

| Method | Endpoint                  | Description        |
| ------ | ------------------------- | ------------------ |
| GET    | `/api/health`             | Health check       |
| GET    | `/api/dashboard`          | Dashboard data     |
| POST   | `/api/predictions`        | Generate forecast  |
| GET    | `/api/forecasts/latest`   | Latest forecast    |
| GET    | `/api/forecasts/history`  | Forecast history   |
| GET    | `/api/alerts`             | Security alerts    |
| PATCH  | `/api/alerts/{id}`        | Update alert       |
| GET    | `/api/network/graph`      | Network topology   |
| GET    | `/api/models/status`      | Model availability |
| GET    | `/api/models/performance` | Model performance  |
| GET    | `/api/replay/status`      | Replay status      |
| POST   | `/api/replay/start`       | Start replay       |
| POST   | `/api/replay/stop`        | Stop replay        |

API documentation:

```text
http://localhost:8000/docs
```

---

## Dataset

This project uses the **CSE-CIC-IDS2018** dataset containing network flow data generated using CICFlowMeter.

The full dataset is kept locally and is not committed to GitHub because of its large size.

```text
data/
├── raw/
├── processed/
└── sample/
```

---

## Model Training

Model training is performed separately using Google Colab.

Trained artifacts are stored in:

```text
models/
├── baseline/
├── xgboost/
├── lstm/
├── transformer/
├── isolation_forest/
└── preprocessing/
```

Model evaluation results are stored in:

```text
experiments/metrics.json
```

---

## Testing

Backend:

```bash
cd backend
pytest tests -v
```

Frontend:

```bash
cd frontend
npm run build
```

---

## Limitations

* Forecast horizon is currently fixed at 5 minutes
* Replay uses historical traffic instead of live network traffic
* Risk thresholds are configurable heuristics
* Demo explanations are rule-based
* Production authentication and RBAC are not included

---

## Future Work

* Live network traffic ingestion
* Kafka-based streaming pipeline
* Multi-horizon attack forecasting
* SHAP-based explanations
* MITRE ATT&CK mapping
* Model drift detection
* MLflow model management
* Authentication and RBAC

---

## License

This project is developed for educational and research purposes under the **SIH26153** problem statement.
