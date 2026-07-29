# Patent & Research Notes

ProcessIQ introduces several novel architectural paradigms suitable for defense or publication in IEEE conferences.

## Novel Claims
1. **Air-gapped LLM Architecture**: 
   ProcessIQ strictly separates deterministic Machine Learning workflows from probabilistic LLM execution. The LLM acts solely as an interpreter/explainer of deterministic metadata artifacts (JSON). This prevents prompt-injection attacks on the ML training cycle and guarantees zero hallucination in model selection or metric reporting.

2. **Deterministic Prediction Planning**: 
   Model recommendations and target detections are generated via a rule-based heuristic scoring engine, explicitly averting the use of LLMs for architectural ML decisions.

3. **Hybrid Edge-Cloud Execution**:
   The platform processes heavy ML computations locally while deferring state and persistence to managed cloud endpoints (Supabase), presenting a cost-effective alternative to multi-tenant cloud AutoML solutions.
