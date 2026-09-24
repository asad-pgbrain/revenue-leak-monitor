"""
Revenue Data Leak Monitor - FastAPI Backend
"""

import os
import json
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Revenue Leak Monitor API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database config
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "revenue",
    "user": "postgres",
    "password": "password"
}

# HubSpot config
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")

@app.get("/")
def root():
    return {"message": "Revenue Leak Monitor API is running."}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/hubspot/deals")
async def get_hubspot_deals():
    """Fetch deals from HubSpot using curl"""
    try:
        result = subprocess.run([
            "curl", "-s",
            "https://api.hubapi.com/crm/v3/objects/deals?limit=10&properties=dealname,amount,dealstage,closedate",
            "-H", f"Authorization: Bearer {HUBSPOT_API_KEY}"
        ], capture_output=True, text=True)
        
        return json.loads(result.stdout)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hubspot/contacts")
async def get_hubspot_contacts():
    """Fetch contacts from HubSpot using curl"""
    try:
        result = subprocess.run([
            "curl", "-s",
            "https://api.hubapi.com/crm/v3/objects/contacts?limit=10&properties=email,firstname,lastname",
            "-H", f"Authorization: Bearer {HUBSPOT_API_KEY}"
        ], capture_output=True, text=True)
        
        return json.loads(result.stdout)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
