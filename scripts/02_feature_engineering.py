# =============================================================
# 02_feature_engineering.py
# Build enriched analytical tables from cleaned data.
# Produces one master account-level table for Power BI.
# =============================================================

import pandas as pd
import numpy as np
import os

PROCESSED = "data/processed"

# ── Load cleaned tables ────────────────────────────────────────
print("Loading cleaned tables...")
accounts = pd.read_csv(f"{PROCESSED}/account_churn_status.csv",     parse_dates=["signup_date"])
subs     = pd.read_csv(f"{PROCESSED}/subscriptions_clean.csv",      parse_dates=["start_date", "end_date"])
usage    = pd.read_csv(f"{PROCESSED}/feature_usage_clean.csv",       parse_dates=["usage_date"])
tickets  = pd.read_csv(f"{PROCESSED}/support_tickets_clean.csv",     parse_dates=["submitted_at"])
churn    = pd.read_csv(f"{PROCESSED}/churn_events_clean.csv",        parse_dates=["churn_date"])


# =============================================================
# BLOCK A: SUBSCRIPTION AGGREGATES (per account)
# =============================================================
print("\n[A] Aggregating subscription data per account...")

sub_agg = subs.groupby("account_id").agg(
    total_subscriptions     = ("subscription_id",  "count"),
    churned_subscriptions   = ("churn_flag",        "sum"),
    total_mrr               = ("mrr_amount",        "sum"),
    avg_mrr                 = ("mrr_amount",        "mean"),
    total_arr               = ("arr_amount",        "sum"),
    max_tenure_months       = ("tenure_months",     "max"),
    avg_tenure_months       = ("tenure_months",     "mean"),
    has_upgraded            = ("upgrade_flag",      "max"),
    has_downgraded          = ("downgrade_flag",    "max"),
    is_trial                = ("is_trial",          "max"),
    auto_renew_count        = ("auto_renew_flag",   "sum"),
).reset_index()

sub_agg["sub_churn_rate"] = (
    sub_agg["churned_subscriptions"] / sub_agg["total_subscriptions"]
).round(3)


# =============================================================
# BLOCK B: FEATURE USAGE AGGREGATES (per account via subscription)
# =============================================================
print("[B] Aggregating feature usage per account...")

# Link subscription → account
usage_with_account = usage.merge(
    subs[["subscription_id", "account_id"]], on="subscription_id", how="left"
)

usage_agg = usage_with_account.groupby("account_id").agg(
    total_usage_events      = ("usage_id",              "count"),
    total_usage_count       = ("usage_count",           "sum"),
    total_usage_duration    = ("usage_duration_secs",   "sum"),
    avg_usage_duration      = ("usage_duration_secs",   "mean"),
    total_errors            = ("error_count",           "sum"),
    unique_features_used    = ("feature_name",          "nunique"),
    beta_feature_usage      = ("is_beta_feature",       "sum"),
).reset_index()

# Engagement score: weighted combo of feature breadth and usage volume (0-100)
usage_agg["engagement_score"] = (
    (usage_agg["unique_features_used"]  / usage_agg["unique_features_used"].max()  * 50) +
    (usage_agg["total_usage_count"]     / usage_agg["total_usage_count"].max()     * 50)
).round(2)


# =============================================================
# BLOCK C: SUPPORT TICKET AGGREGATES (per account)
# =============================================================
print("[C] Aggregating support tickets per account...")

ticket_agg = tickets.groupby("account_id").agg(
    total_tickets               = ("ticket_id",                     "count"),
    escalated_tickets           = ("escalation_flag",               "sum"),
    avg_resolution_hours        = ("resolution_time_hours",         "mean"),
    avg_first_response_mins     = ("first_response_time_minutes",   "mean"),
    avg_satisfaction            = ("satisfaction_score_filled",     "mean"),
    urgent_tickets              = ("priority",                      lambda x: (x == "urgent").sum()),
).reset_index()

ticket_agg["escalation_rate"] = (
    ticket_agg["escalated_tickets"] / ticket_agg["total_tickets"]
).round(3)

ticket_agg = ticket_agg.round(2)


# =============================================================
# BLOCK D: TENURE GROUPS & FEATURE BINS
# =============================================================
print("[D] Building tenure groups and feature bins...")

def tenure_group(t):
    if   t <= 3:  return "0-3 Months"
    elif t <= 6:  return "4-6 Months"
    elif t <= 12: return "7-12 Months"
    elif t <= 24: return "13-24 Months"
    else:         return "24+ Months"

tenure_order = ["0-3 Months", "4-6 Months", "7-12 Months", "13-24 Months", "24+ Months"]


# =============================================================
# BLOCK E: JOIN EVERYTHING INTO MASTER TABLE
# =============================================================
print("[E] Building master account table...")

master = accounts.copy()
master = master.merge(sub_agg,    on="account_id", how="left")
master = master.merge(usage_agg,  on="account_id", how="left")
master = master.merge(ticket_agg, on="account_id", how="left")

# Fill accounts with no usage/ticket records
master["total_usage_events"]   = master["total_usage_events"].fillna(0)
master["unique_features_used"] = master["unique_features_used"].fillna(0)
master["engagement_score"]     = master["engagement_score"].fillna(0)
master["total_tickets"]        = master["total_tickets"].fillna(0)
master["total_errors"]         = master["total_errors"].fillna(0)

# Derived columns
master["TenureGroup"] = master["max_tenure_months"].apply(tenure_group)
master["TenureGroup"] = pd.Categorical(master["TenureGroup"], categories=tenure_order, ordered=True)

master["signup_month"]  = master["signup_date"].dt.to_period("M").astype(str)
master["signup_year"]   = master["signup_date"].dt.year
master["signup_quarter"]= master["signup_date"].dt.to_period("Q").astype(str)

master["RevenueTier"] = pd.qcut(
    master["total_mrr"].rank(method="first"),
    q=4,
    labels=["Low", "Medium", "High", "Very High"]
)

master["EngagementTier"] = pd.cut(
    master["engagement_score"],
    bins=[-1, 25, 50, 75, 100],
    labels=["Very Low", "Low", "Medium", "High"]
)

master["CLV"] = (master["avg_tenure_months"] * master["avg_mrr"]).round(2)

master["HighRisk"] = (
    (master["engagement_score"] < 25) &
    (master["plan_tier"].isin(["Basic", "Free"])) &
    (master["max_tenure_months"] <= 3)
).astype(int)

# Save
master.to_csv(f"{PROCESSED}/master_accounts.csv", index=False)
print(f"  Saved → master_accounts.csv  ({master.shape[0]} rows × {master.shape[1]} cols)")

print("\n✓ Feature engineering complete.")