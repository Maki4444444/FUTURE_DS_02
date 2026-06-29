# =============================================================
# 04_cohort_analysis.py
# Build signup-month cohort retention table and summary.
# =============================================================

import pandas as pd
import numpy as np
import os

PROCESSED = "data/processed"

print("Loading master table...")
master = pd.read_csv(f"{PROCESSED}/master_accounts.csv", parse_dates=["signup_date"])


# =============================================================
# COHORT TABLE: one row per signup_month
# =============================================================
print("\n[1] Building cohort summary by signup month...")

cohort = master.groupby("signup_month").agg(
    TotalAccounts   = ("is_churned",        "count"),
    Churned         = ("is_churned",        "sum"),
    AvgTenure       = ("max_tenure_months", "mean"),
    AvgMRR          = ("avg_mrr",           "mean"),
    TotalMRR        = ("total_mrr",         "sum"),
    AvgCLV          = ("CLV",               "mean"),
    AvgEngagement   = ("engagement_score",  "mean"),
).reset_index()

cohort["Retained"]          = cohort["TotalAccounts"] - cohort["Churned"]
cohort["ChurnRate_pct"]     = (cohort["Churned"] / cohort["TotalAccounts"] * 100).round(2)
cohort["RetentionRate_pct"] = (100 - cohort["ChurnRate_pct"]).round(2)
cohort["MRRLost"]           = (
    master[master["is_churned"]==True]
    .groupby("signup_month")["total_mrr"]
    .sum()
    .reset_index()
    .rename(columns={"total_mrr": "MRRLost"})
    .set_index("signup_month")["MRRLost"]
    .reindex(cohort["signup_month"])
    .fillna(0)
    .values
)

cohort = cohort.sort_values("signup_month")
cohort = cohort.round(2)

print(cohort[["signup_month", "TotalAccounts", "Churned",
              "ChurnRate_pct", "RetentionRate_pct", "AvgTenure", "MRRLost"]].to_string(index=False))

cohort.to_csv(f"{PROCESSED}/cohort_retention.csv", index=False)
print("  Saved → cohort_retention.csv")


# =============================================================
# COHORT TABLE: by signup quarter (for trend line in Power BI)
# =============================================================
print("\n[2] Building cohort summary by signup quarter...")

cohort_q = master.groupby("signup_quarter").agg(
    TotalAccounts   = ("is_churned",        "count"),
    Churned         = ("is_churned",        "sum"),
    AvgTenure       = ("max_tenure_months", "mean"),
    TotalMRR        = ("total_mrr",         "sum"),
    AvgCLV          = ("CLV",               "mean"),
).reset_index()

cohort_q["Retained"]            = cohort_q["TotalAccounts"] - cohort_q["Churned"]
cohort_q["ChurnRate_pct"]       = (cohort_q["Churned"] / cohort_q["TotalAccounts"] * 100).round(2)
cohort_q["RetentionRate_pct"]   = (100 - cohort_q["ChurnRate_pct"]).round(2)
cohort_q = cohort_q.sort_values("signup_quarter").round(2)

print(cohort_q.to_string(index=False))

cohort_q.to_csv(f"{PROCESSED}/cohort_by_quarter.csv", index=False)
print("  Saved → cohort_by_quarter.csv")


# =============================================================
# PLAN TIER × TENURE GROUP CROSS TABLE (heatmap source)
# =============================================================
print("\n[3] Building plan tier × tenure group churn heatmap...")

tenure_order = ["0-3 Months", "4-6 Months", "7-12 Months", "13-24 Months", "24+ Months"]

heatmap = master.groupby(["plan_tier", "TenureGroup"])["is_churned"].agg(
    Churned="sum",
    Total="count"
).reset_index()

heatmap["ChurnRate_pct"] = (heatmap["Churned"] / heatmap["Total"] * 100).round(2)
heatmap["TenureGroup"]   = pd.Categorical(heatmap["TenureGroup"], categories=tenure_order, ordered=True)
heatmap = heatmap.sort_values(["plan_tier", "TenureGroup"])

print(heatmap.to_string(index=False))

heatmap.to_csv(f"{PROCESSED}/churn_heatmap.csv", index=False)
print("  Saved → churn_heatmap.csv")


print("\n✓ Cohort analysis complete.")