# ProcessIQ: Intelligent Data Preprocessing & AutoML Platform

ProcessIQ is a modern, high-performance web application designed to automate dataset cleaning, feature engineering, and predictive model training. It enables users to upload raw industrial datasets, clean and scale them deterministically, run feature importance checks, and orchestrate parallel AutoML training pipelines.

---

## 🚀 Key Features

*   **⚡ Zero-Lag Data Upload**: Instant local storage upload support for both CSV and Excel (`.xlsx`, `.xls`) files.
*   **⚙️ Deterministic Preprocessing Pipeline**: Automatically applies missing value imputation, min-max feature scaling, and one-hot encoding for categorical variables.
*   **📊 Interactive Data Visualizations**: Beautiful Plotly-powered feature distribution charts and summary stats.
*   **📑 Reports & Quality Center**: Real-time summary dashboard and downloadable Markdown reports detailing data quality improvements.
*   **🧠 Parallel AutoML Engine**: Dispatches candidate classifiers and regressors (Logistic Regression, Random Forest, XGBoost, etc.) in parallel thread pools with automatic multi-class evaluation fallback.
*   **⬇️ Download Center**: Download clean, scaled, model-ready datasets (`.csv`) and pipeline reports directly to your computer.

---

## 🛠️ Technology Stack

*   **Frontend**: Next.js 14 (App Router), React, TypeScript, React Query (v5), TailwindCSS, Shadcn UI, Plotly.
*   **Backend**: FastAPI, Python 3.11+, SQLAlchemy, PostgreSQL, Redis.
*   **Task Queue**: Celery (asynchronous preprocessing & model training).
*   **Machine Learning**: Scikit-learn, XGBoost, LightGBM, CatBoost.

---

## 🔧 Installation & Setup

### Prerequisites
Make sure you have the following installed on your machine:
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   [Python 3.10+](https://www.python.org/downloads/)
*   [Node.js 18+](https://nodejs.org/)

---

### Step 1: Environment Setup
1. Copy the environment template file:
    ```bash
    cp .env.example .env
    ```
2. Open `.env` and fill in your details (database credentials, Redis URL, and optional LLM keys).

---

### Step 2: Spin Up Infrastructure
Start the PostgreSQL database and Redis container in the background:
```bash
docker-compose up -d
```

---

### Step 3: Run the Backend Services
1. **Activate Virtual Environment** (optional but recommended):
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On Mac/Linux
    ```
2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3. **Start the Celery Task Worker**:
    ```bash
    py -m celery -A backend.workers.celery_app worker --loglevel=info -P solo
    ```
4. **Start the FastAPI Backend Server**:
    ```bash
    py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ```

---

### Step 4: Run the Frontend
1. Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2. Install npm packages:
    ```bash
    npm install
    ```
3. Start the Next.js development server:
    ```bash
    npm run dev
    ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Running Tests
Verify that all platform components pass unit and integration tests:
```bash
$env:PYTHONPATH="."
pytest
```
