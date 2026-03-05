import os, sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
url = os.getenv('SUPABASE_URL', '').replace('postgres://', 'postgresql://', 1)

if not url:
    print("ERROR: SUPABASE_URL not found in .env")
    sys.exit(1)

print(f"Connecting to database...")
engine = create_engine(url)

tables = [
    'billing', 'workers', 'attendance', 'finance_expenses', 'sales_orders',
    'accounting_ledger', 'marketing_campaigns', 'rental_bookings',
    'restaurant_sales', 'marketing_leads', 'hr_leaverequests', 'hr_payroll', 'finance_invoices'
]

with engine.connect() as conn:
    for t in tables:
        try:
            conn.execute(text(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS username TEXT DEFAULT ''"))
            conn.commit()
            print(f"  OK: Added username column to '{t}'")
        except Exception as e:
            conn.rollback()
            print(f"  SKIP/ERROR {t}: {e}")

print("\nMigration complete!")
