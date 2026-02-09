from backend.database import SessionLocal
from backend.models import Transaction, Budget

db = SessionLocal()
try:
    count_t = db.query(Transaction).count()
    count_b = db.query(Budget).count()
    print(f"Transactions: {count_t}")
    print(f"Budgets: {count_b}")
    
    # Print last 5 transactions
    txs = db.query(Transaction).all()[-5:]
    for t in txs:
        print(f" - {t.id}: {t.description} | {t.amount}")
finally:
    db.close()
