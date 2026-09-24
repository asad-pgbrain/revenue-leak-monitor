# Revenue Leak Monitor

Detects revenue mismatches between Stripe and CRM (HubSpot/Salesforce) with monetary impact.

## Features
- 🔍 12 reconciliation queries (Won-but-Unpaid, MRR Drift, Silent Churn, etc.)
- 💰 Monetary impact calculation
- 📢 Slack alerts with owner assignment
- 📊 Dashboard with mismatch trends

## Tech Stack
- Backend: FastAPI, Python, PostgreSQL
- Data: dbt, Airflow, dlt
- Integrations: Stripe API, HubSpot API, Slack API
- Deployment: Docker, Railway

## Setup
1. Clone repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add keys
6. Run: `uvicorn main:app --reload`
