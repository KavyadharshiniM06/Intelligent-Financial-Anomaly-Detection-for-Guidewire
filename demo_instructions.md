# 📋 Professional Demo Guide: Intelligent Claim Risk Engine

This guide provide the exact sequence of commands and talking points to demonstrate the **Intelligent Financial Anomaly Detection for Guidewire** system to evaluators.

---

## 🎯 Demo Objectives
1.  **Connectivity**: Show the frontend talking to the FastAPI backend.
2.  **Risk Evaluation**: Demonstrate how a claim is processed through ML and Rule engines.
3.  **Explainability**: Explain *why* a decision was made (Risk Score + Reasons).
4.  **Audit Trail**: Verify that decisions are persisted for compliance.

---

## 1. BACKEND SETUP (Terminal 1)

### A. Environment & Dependencies
```bash
cd backend
# Ensure virtual environment is active
# Windows: venv\Scripts\activate
# Unix: source venv/bin/activate

pip install -r requirements.txt
```

### B. Database Initialization (Local PostgreSQL)
Ensure your local PostgreSQL is running and you have created a database named `insurance_claims` on port **5433**.

```bash
# 1. Sync the schema (Adds missing columns like 'age', 'vehicle_age')
python -m app.db.sync_schema

# 2. Seed demo data (Creates the demo customer and policy)
python -m app.db.seed_demo
```
**Expected Output**: `--- ✅ Demo Data Seeded Successfully ---` with Customer ID `3` and Policy ID `2`.

### C. Start Server
```bash
uvicorn app.main:app --reload
```
**Verification**: Open [http://localhost:8000/docs](http://localhost:8000/docs) to see the Swagger UI.

---

## 2. FRONTEND SETUP (Terminal 2)

```bash
cd frontend
# Serve the console using Python's built-in server
python -m http.server 3000
```
**Access**: Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 3. DEMO FLOW: ARCHETYPE SCENARIOS

### Step 1: Connectivity Check
1.  In the React Console, ensure the **Backend Base URL** is `http://127.0.0.1:8000`.
2.  Click **Run Health Check**.
3.  **Talking Point**: *"First, we verify the operational status of our risk services and database connectivity. A green status ensures the pipeline is ready for ingestion."*

### Step 2: "The Safe Executive" (APPROVE)
1.  **Input**: Customer ID `4`, Policy ID `3`, Amount `500` (Niranjan).
2.  **Expected Decision**: `APPROVE` (Risk Score < 0.3).
3.  **Talking Point**: *"Meet **Niranjan**. A long-standing customer with a premium NCAP 5 vehicle. The RandomForest model rewards his stability and safety profile, while the Rule Engine applies a 'Safety Bonus' for his car choice."*

### Step 3: "The Risky Rookie" (INVESTIGATE)
1.  **Input**: Customer ID `5`, Policy ID `4`, Amount `4500` (Rahul).
2.  **Expected Decision**: `INVESTIGATE` (0.3 < Risk Score < 0.7).
3.  **Talking Point**: *"Now consider **Rahul**. He's a new policyholder (less than 14 days) with a low-safety vehicle (NCAP 2). The system flags this as suspicious, moving it from auto-approval to manual investigation for more scrutiny."*

### Step 4: "Urban Density High-Risk" (REJECT)
1.  **Input**: Customer ID `6`, Policy ID `5`, Amount `15000`, Severity: `total loss` (Kavya).
2.  **Expected Decision**: `REJECT` (Risk Score > 0.7).
3.  **Talking Point**: *"Finally, **Kavya**. She operates in a high-density urban region and is reporting a total loss claim for a high amount. Combined with her history of frequent small claims (seeded in the background), the ML model identifies a high-risk pattern and automatically rejects the claim."*

### Step 5: "Ghost Claim" (ERROR HANDLING)
1.  **Input**: Customer ID `999`, Policy ID `999`, Amount `100`.
2.  **Click**: `Submit to Risk Engine`.
3.  **Expected Result**: Error feedback (e.g., "Policy not found").
4.  **Talking Point**: *"Our system is also built with robust error-handling. If an adjuster enters an invalid ID or a policy that doesn't exist, the system catches the exception and provides clear feedback, preventing corrupted data from entering the risk pipeline."*

---

## 4. AUDIT & EXPLAINABILITY
1.  Note the **Claim ID** from a submission (e.g., `3`).
2.  Go to the **Lookup Audit** section in the UI.
3.  Enter the Claim ID and click **Fetch Audit**.
4.  **Talking Point**: *"Finally, every decision is logged with a high-fidelity audit trail. We store the risk score, the final decision, and the specific reasons (e.g., 'Claim amount exceeds policy threshold'). This is critical for regulatory compliance and adjuster reviews."*

---

## 5. DEBUGGING & TROUBLESHOOTING

-   **Backend not starting**: Verify `DATABASE_URL` in `.env` is correct. Check if port `8000` is already in use.
-   **CORS Error**: Ensure you have restarted the backend after the latest `main.py` updates.
-   **Model not loading**: Ensure `model.pkl` and `scaler.pkl` are present in `backend/app/services/`.
-   **404 Policy Not Found**: Ensure you have run the `seed_demo` script.

---

## 6. FINAL PERFORMANCE NOTES
-   **No Runtime Training**: The model is pre-trained and loaded into memory at startup for sub-50ms inference.
-   **Assumptions**: We assume the local PostgreSQL is initialized via `seed_demo.py`.
-   **Limitations**: Real-time behavioral transaction signals (PaySim) are mocked for this phase of the demo but can be enabled in the `inference_payload`.
