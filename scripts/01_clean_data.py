# =============================================================
# 01_clean_data.py
# Load all 5 raw tables, clean each individually, and save
# cleaned versions to data/processed/
# =============================================================

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────
RAW = "data/raw"
PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)

# ── 1. Load all tables ─────────────────────────────────────────
print("Loading raw tables...")
accounts = pd.read_csv(f"{RAW}/ravenstack_accounts.csv")
subs     = pd.read_csv(f"{RAW}/ravenstack_subscriptions.csv")
usage    = pd.read_csv(f"{RAW}/ravenstack_feature_usage.csv")
tickets  = pd.read_csv(f"{RAW}/ravenstack_support_tickets.csv")
churn    = pd.read_csv(f"{RAW}/ravenstack_churn_events.csv")

print(f"  accounts        : {accounts.shape}")
print(f"  subscriptions   : {subs.shape}")
print(f"  feature_usage   : {usage.shape}")
print(f"  support_tickets : {tickets.shape}")
print(f"  churn_events    : {churn.shape}")


# =============================================================
# TABLE 1: ACCOUNTS
# =============================================================
print("\n[1/5] Cleaning accounts...")

# Parse dates
accounts["signup_date"] = pd.to_datetime(accounts["signup_date"], errors="coerce")

# Strip whitespace from string columns
str_cols = accounts.select_dtypes("object").columns
accounts[str_cols] = accounts[str_cols].apply(lambda c: c.str.strip())

# Standardise categorical casing
accounts["industry"]        = accounts["industry"].str.title()
accounts["country"]         = accounts["country"].str.upper()
accounts["plan_tier"]       = accounts["plan_tier"].str.title()
accounts["referral_source"] = accounts["referral_source"].str.lower()

# Missing value check
print(f"  Nulls:\n{accounts.isnull().sum()}")
print(f"  Duplicates: {accounts.duplicated().sum()}")

accounts.to_csv(f"{PROCESSED}/accounts_clean.csv", index=False)
print("  Saved → accounts_clean.csv")


# =============================================================
# TABLE 2: SUBSCRIPTIONS
# =============================================================
print("\n[2/5] Cleaning subscriptions...")

subs["start_date"] = pd.to_datetime(subs["start_date"], errors="coerce")
subs["end_date"]   = pd.to_datetime(subs["end_date"],   errors="coerce")

str_cols = subs.select_dtypes("object").columns
subs[str_cols] = subs[str_cols].apply(lambda c: c.str.strip())

subs["plan_tier"]          = subs["plan_tier"].str.title()
subs["billing_frequency"]  = subs["billing_frequency"].str.lower()

# Tenure in months: end_date if churned, else today
reference_date = pd.Timestamp.today().normalize()
subs["tenure_months"] = subs.apply(
    lambda r: (
        (r["end_date"] - r["start_date"]).days / 30
        if pd.notnull(r["end_date"])
        else (reference_date - r["start_date"]).days / 30
    ),
    axis=1
).round(1)

print(f"  Nulls:\n{subs.isnull().sum()}")
print(f"  Duplicates: {subs.duplicated().sum()}")

subs.to_csv(f"{PROCESSED}/subscriptions_clean.csv", index=False)
print("  Saved → subscriptions_clean.csv")


# =============================================================
# TABLE 3: FEATURE USAGE
# =============================================================
print("\n[3/5] Cleaning feature_usage...")

usage["usage_date"] = pd.to_datetime(usage["usage_date"], errors="coerce")

str_cols = usage.select_dtypes("object").columns
usage[str_cols] = usage[str_cols].apply(lambda c: c.str.strip())

usage["feature_name"] = usage["feature_name"].str.lower()

# Cap extreme error counts at 99th percentile (outlier guard)
p99 = usage["error_count"].quantile(0.99)
usage["error_count"] = usage["error_count"].clip(upper=p99)

print(f"  Nulls:\n{usage.isnull().sum()}")
print(f"  Duplicates: {usage.duplicated(subset='usage_id').sum()}")

usage.to_csv(f"{PROCESSED}/feature_usage_clean.csv", index=False)
print("  Saved → feature_usage_clean.csv")


# =============================================================
# TABLE 4: SUPPORT TICKETS
# =============================================================
print("\n[4/5] Cleaning support_tickets...")

tickets["submitted_at"] = pd.to_datetime(tickets["submitted_at"], errors="coerce")
tickets["closed_at"]    = pd.to_datetime(tickets["closed_at"],    errors="coerce")

str_cols = tickets.select_dtypes("object").columns
tickets[str_cols] = tickets[str_cols].apply(lambda c: c.str.strip())

tickets["priority"] = tickets["priority"].str.lower()

# satisfaction_score: fill nulls with median (62% null — flag, don't drop)
sat_median = tickets["satisfaction_score"].median()
tickets["satisfaction_score_filled"] = tickets["satisfaction_score"].fillna(sat_median)
tickets["satisfaction_missing_flag"] = tickets["satisfaction_score"].isnull().astype(int)

print(f"  Nulls:\n{tickets.isnull().sum()}")
print(f"  Duplicates: {tickets.duplicated(subset='ticket_id').sum()}")

tickets.to_csv(f"{PROCESSED}/support_tickets_clean.csv", index=False)
print("  Saved → support_tickets_clean.csv")


# =============================================================
# TABLE 5: CHURN EVENTS
# =============================================================
print("\n[5/5] Cleaning churn_events...")

churn["churn_date"] = pd.to_datetime(churn["churn_date"], errors="coerce")

str_cols = churn.select_dtypes("object").columns
churn[str_cols] = churn[str_cols].apply(lambda c: c.str.strip())

churn["reason_code"] = churn["reason_code"].str.lower()

# Fill missing refund as 0 (no refund given)
churn["refund_amount_usd"] = churn["refund_amount_usd"].fillna(0)

# Fill missing feedback as "no feedback"
churn["feedback_text"] = churn["feedback_text"].fillna("no feedback")

print(f"  Nulls:\n{churn.isnull().sum()}")
print(f"  Duplicates: {churn.duplicated(subset='churn_event_id').sum()}")

churn.to_csv(f"{PROCESSED}/churn_events_clean.csv", index=False)
print("  Saved → churn_events_clean.csv")


# =============================================================
# DERIVE ACCOUNT-LEVEL CHURN STATUS (Option B: accounts.churn_flag)
# One row per account — safe grain for all downstream joins
# =============================================================
print("\nDeriving account-level churn status...")

account_churn_status = accounts[[
    "account_id", "account_name", "industry", "country",
    "signup_date", "referral_source", "plan_tier",
    "seats", "is_trial", "churn_flag"
]].copy()

account_churn_status.rename(columns={"churn_flag": "is_churned"}, inplace=True)

account_churn_status.to_csv(f"{PROCESSED}/account_churn_status.csv", index=False)
print("  Saved → account_churn_status.csv")

print("\n✓ All cleaning complete. Files in data/processed/:")
for f in sorted(os.listdir(PROCESSED)):
    print(f"  {f}")