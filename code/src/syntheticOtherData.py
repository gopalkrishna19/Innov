import os
import random
from datetime import datetime, timedelta, timezone

import pandas as pd

# Load existing user_ids from previous login data
login_df = pd.read_excel("code/src/synthetic_login_metadata.xlsx")
user_ids = login_df["user_id"].unique()

# Constants
NUM_SESSIONS = 1000
NUM_TRANSACTIONS = 1500
NUM_FEATURES = 2000

pages = ["dashboard", "transfer", "settings", "profile", "offers", "support"]
transaction_types = ["fund_transfer", "bill_payment", "recharge", "upi_payment"]
transaction_methods = ["NEFT", "IMPS", "RTGS", "UPI"]
features = ["balance_check", "mini_statement", "set_pin", "block_card", "credit_score", "loan_offers"]

# Generate Session Metadata
def generate_session_data():
    session_data = []
    for _ in range(NUM_SESSIONS):
        user_id = random.choice(user_ids)
        session_duration = round(random.uniform(30, 900), 2)  # seconds
        num_pages = random.randint(2, 6)
        visited = random.sample(pages, num_pages)
        timestamp = datetime.utcnow() - timedelta(minutes=random.randint(0, 100000))
        session_data.append({
            "user_id": user_id,
            "timestamp": timestamp.isoformat() + "Z",
            "session_duration_sec": session_duration,
            "pages_visited": " > ".join(visited)
        })
    return pd.DataFrame(session_data)

# Generate Transaction Metadata
def generate_transaction_data():
    transaction_data = []
    for _ in range(NUM_TRANSACTIONS):
        user_id = random.choice(user_ids)
        t_type = random.choice(transaction_types)
        method = random.choice(transaction_methods)
        amount = round(random.uniform(10, 5000), 2)
        recipient = f"ACC{random.randint(10000, 99999)}"
        timestamp = datetime.utcnow() - timedelta(minutes=random.randint(0, 100000))
        transaction_data.append({
            "user_id": user_id,
            "timestamp": timestamp.isoformat() + "Z",
            "transaction_type": t_type,
            "amount": amount,
            "recipient": recipient,
            "method": method
        })
    return pd.DataFrame(transaction_data)

# Generate Feature Usage Logs
def generate_feature_usage_data():
    feature_data = []
    for _ in range(NUM_FEATURES):
        user_id = random.choice(user_ids)
        feature = random.choice(features)
        usage_count = random.randint(1, 10)
        timestamp = datetime.utcnow() - timedelta(minutes=random.randint(0, 100000))
        feature_data.append({
            "user_id": user_id,
            "timestamp": timestamp.isoformat() + "Z",
            "feature": feature,
            "frequency": usage_count
        })
    return pd.DataFrame(feature_data)

# Create dataframes
session_df = generate_session_data()
transaction_df = generate_transaction_data()
feature_df = generate_feature_usage_data()

# Save to Excel files
os.makedirs("synthetic_logs", exist_ok=True)
session_df.to_excel("synthetic_logs/session_metadata.xlsx", index=False)
transaction_df.to_excel("synthetic_logs/transaction_metadata.xlsx", index=False)
feature_df.to_excel("synthetic_logs/feature_usage_logs.xlsx", index=False)

session_df.head(), transaction_df.head(), feature_df.head()
