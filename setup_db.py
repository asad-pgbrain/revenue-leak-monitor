"""
Revenue Leak Monitor - Database Setup
"""

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "revenue",
    "user": "postgres",
    "password": "password"
}

def setup_database():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Customers table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            owner_id TEXT NOT NULL,
            email TEXT NOT NULL,
            name TEXT,
            stripe_id TEXT,
            crm_id TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    
    # Stripe charges
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stripe_charges (
            id SERIAL PRIMARY KEY,
            owner_id TEXT NOT NULL,
            customer_id INTEGER REFERENCES customers(id),
            charge_id TEXT NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            currency TEXT DEFAULT 'USD',
            status TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    
    # CRM deals
    cur.execute("""
        CREATE TABLE IF NOT EXISTS crm_deals (
            id SERIAL PRIMARY KEY,
            owner_id TEXT NOT NULL,
            customer_id INTEGER REFERENCES customers(id),
            deal_id TEXT NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            stage TEXT NOT NULL,
            closed_at TIMESTAMPTZ
        );
    """)
    
    # Mismatches
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mismatches (
            id SERIAL PRIMARY KEY,
            owner_id TEXT NOT NULL,
            mismatch_type TEXT NOT NULL,
            stripe_value DECIMAL(12,2),
            crm_value DECIMAL(12,2),
            impact DECIMAL(12,2) NOT NULL,
            severity TEXT CHECK (severity IN ('P1', 'P2', 'P3', 'INFO')),
            owner_assignee TEXT,
            status TEXT DEFAULT 'open',
            detected_at TIMESTAMPTZ DEFAULT NOW(),
            resolved_at TIMESTAMPTZ
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database setup complete!")

if __name__ == "__main__":
    setup_database()
