"""
Revenue Data Leak Monitor - Data Sync
Stripe + HubSpot data to PostgreSQL
"""

import os
import json
import subprocess
import psycopg2
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "revenue",
    "user": "postgres",
    "password": "password"
}

OWNER_ID = "owner_1"

def sync_stripe_customers():
    """Stripe customers ko database mein store karein"""
    print("🔄 Syncing Stripe customers...")
    customers = stripe.Customer.list(limit=100)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    count = 0
    for customer in customers.data:
        cur.execute("""
            INSERT INTO customers (owner_id, email, name, stripe_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (OWNER_ID, customer.email, customer.name, customer.id))
        count += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"  ✅ {count} Stripe customers synced")

def sync_stripe_charges():
    """Stripe charges ko database mein store karein"""
    print("🔄 Syncing Stripe charges...")
    charges = stripe.Charge.list(limit=100)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    count = 0
    for charge in charges.data:
        cur.execute("""
            INSERT INTO stripe_charges (owner_id, charge_id, amount, currency, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (OWNER_ID, charge.id, charge.amount / 100, charge.currency, charge.status))
        count += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"  ✅ {count} Stripe charges synced")

def sync_hubspot_deals():
    """HubSpot deals ko database mein store karein"""
    print("🔄 Syncing HubSpot deals...")
    result = subprocess.run([
        "curl", "-s",
        "https://api.hubapi.com/crm/v3/objects/deals?limit=100&properties=dealname,amount,dealstage,closedate",
        "-H", f"Authorization: Bearer {HUBSPOT_API_KEY}"
    ], capture_output=True, text=True)
    
    data = json.loads(result.stdout)
    deals = data.get("results", [])
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    count = 0
    for deal in deals:
        props = deal.get("properties", {})
        cur.execute("""
            INSERT INTO crm_deals (owner_id, deal_id, amount, stage)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (OWNER_ID, deal["id"], props.get("amount", 0) or 0, props.get("dealstage", "")))
        count += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"  ✅ {count} HubSpot deals synced")

def sync_hubspot_contacts():
    """HubSpot contacts ko database mein store karein"""
    print("🔄 Syncing HubSpot contacts...")
    result = subprocess.run([
        "curl", "-s",
        "https://api.hubapi.com/crm/v3/objects/contacts?limit=100&properties=email,firstname,lastname",
        "-H", f"Authorization: Bearer {HUBSPOT_API_KEY}"
    ], capture_output=True, text=True)
    
    data = json.loads(result.stdout)
    contacts = data.get("results", [])
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    count = 0
    for contact in contacts:
        props = contact.get("properties", {})
        email = props.get("email", "")
        name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
        cur.execute("""
            INSERT INTO customers (owner_id, email, name, crm_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (OWNER_ID, email, name, contact["id"]))
        count += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"  ✅ {count} HubSpot contacts synced")

if __name__ == "__main__":
    print("🚀 Starting data sync...")
    print("=" * 50)
    sync_stripe_customers()
    sync_stripe_charges()
    sync_hubspot_deals()
    sync_hubspot_contacts()
    print("=" * 50)
    print("🎉 Data sync complete!")
