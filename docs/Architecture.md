# ProcessIQ Architecture

ProcessIQ is designed as an end-to-end AI-assisted Machine Learning Lifecycle Platform.

## Core Philosophy
1. **Deterministic Core:** The Analytics Engine, Prediction Planner, and AutoML Orchestrator are purely deterministic.
2. **AI as an Interpreter:** The LLM (Intelligent Copilot) is strictly an overlay. It never touches raw data or makes ML decisions directly; it only reads deterministic artifacts (JSON metadata, reports) and explains them.
3. **Pluggable Storage:** ProcessIQ natively supports local disk storage or Supabase Storage via the `StorageBackend` abstraction.
4. **Local Compute First:** Computation happens natively on the host machine to maximize performance and avoid cloud costs during the prototyping/development phases.

## High-Level Architecture

```text
                     Browser
                         │
                 localhost:3000
                     Next.js
                         │
                    FastAPI API
                 localhost:8000
                         │
 ┌──────────────┬──────────────┬───────────────┬──────────────┐
 │              │              │               │              │
Analytics   Prediction      AutoML         Copilot       Artifact
 Engine       Planner     Orchestrator    (Gemini)       Service
 │              │              │               │              │
 └──────────────┴──────────────┴───────────────┘              │
                                                              │
                         ┌────────────────────────────────────┴────────────┐
                         │                                                 │
                         ▼                                                 ▼
                LocalStorageBackend                          SupabaseStorageBackend
```

## Technologies
- **Frontend**: Next.js, TailwindCSS, React Query, Plotly.js
- **Backend**: FastAPI, SQLAlchemy, Celery, Pydantic
- **ML Stack**: Pandas, Scikit-learn, XGBoost, LightGBM, CatBoost
- **Infrastructure**: Redis (Queue), Supabase PostgreSQL, Supabase Storage
