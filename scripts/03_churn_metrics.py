# =============================================================
# 03_churn_metrics.py
# Compute all core churn KPIs and segment breakdowns.
# Saves outputs for Power BI and docs/insights_summary.md
# =============================================================

import pandas as pd
import numpy as np
import os

PROCESSED = "data/processed"

print("Loading master table...")
master = pd.read_csv(f"{PROCESSED}/master_accounts.csv", parse_dates=["signup_date"])

# ── Helpers ────────────────────────────────────────────────────
def churn_by(col):
    result = master.groupby(col)["is_churned"].agg(["sum", "count"])
    result.columns = ["Churned", "Total"]
    result["Retained"]      = result["Total"] - result["Churned"]
    result["ChurnRate_pct"] = (result["Churned"] / result["Total"] * 100).round(2)
    result["RetentionRate_pct"] = (100 - result["ChurnRate_pct"]).round(2)
    result["AvgMRR"]        = master.groupby(col)["avg_mrr"].mean().round(2)
    result["AvgCLV"]        = master.groupby(col)["CLV"].mean().round(2)
    return result.reset_index().sort_values("ChurnRate_pct", ascending=False)


# =============================================================
# CORE KPIs
# =============================================================
print("\n[1] Core KPIs...")

total      = len(master)
churned    = master["is_churned"].sum()
retained   = total - churned
churn_rate = round(churned / total * 100, 2)
ret_rate   = round(100 - churn_rate, 2)

avg_tenure_active  = master[master["is_churned"]==False]["max_tenure_months"].mean()
avg_tenure_churned = master[master["is_churned"]==True]["max_tenure_months"].mean()
avg_clv_active     = master[master["is_churned"]==False]["CLV"].mean()
avg_clv_churned    = master[master["is_churned"]==True]["CLV"].mean()
total_mrr          = master["total_mrr"].sum()
mrr_at_risk        = master[master["is_churned"]==True]["total_mrr"].sum()
high_risk_count    = master["HighRisk"].sum()

core_metrics = pd.DataFrame({
    "Metric": [
        "Total Accounts", "Churned", "Retained",
        "Churn Rate (%)", "Retention Rate (%)",
        "Avg Tenure - Active (months)", "Avg Tenure - Churned (months)",
        "Avg CLV - Active ($)", "Avg CLV - Churned ($)",
        "Total MRR ($)", "MRR Lost to Churn ($)",
        "High Risk Accounts"
    ],
    "Value": [
        total, int(churned), int(retained),
        churn_rate, ret_rate,
        round(avg_tenure_active, 1), round(avg_tenure_churned, 1),
        round(avg_clv_active, 2), round(avg_clv_churned, 2),
        round(total_mrr, 2), round(mrr_at_risk, 2),
        int(high_risk_count)
    ]
})

print(core_metrics.to_string(index=False))
core_metrics.to_csv(f"{PROCESSED}/core_metrics.csv", index=False)
print("  Saved → core_metrics.csv")


# =============================================================
# SEGMENT BREAKDOWNS
# =============================================================
print("\n[2] Segment breakdowns...")

segments = {
    "plan_tier"       : "By Plan Tier",
    "TenureGroup"     : "By Tenure Group",
    "industry"        : "By Industry",
    "country"         : "By Country",
    "EngagementTier"  : "By Engagement Tier",
    "RevenueTier"     : "By Revenue Tier",
    "referral_source" : "By Referral Source",
}

all_segments = []
for col, label in segments.items():
    df = churn_by(col)
    df.rename(columns={col: "SegmentValue"}, inplace=True)
    df["SegmentType"] = label
    all_segments.append(df)
    print(f"\n  {label}:")
    print(df[["SegmentValue", "Total", "Churned", "ChurnRate_pct", "AvgCLV"]].to_string(index=False))

segment_summary = pd.concat(all_segments, ignore_index=True)
segment_summary.to_csv(f"{PROCESSED}/segment_summary.csv", index=False)
print("\n  Saved → segment_summary.csv")


# =============================================================
# ENGAGEMENT vs CHURN COMPARISON
# =============================================================
print("\n[3] Engagement comparison: churned vs retained...")

engagement_cols = [
    "unique_features_used", "total_usage_count",
    "engagement_score", "total_tickets",
    "avg_satisfaction", "escalation_rate"
]

eng_compare = master.groupby("is_churned")[engagement_cols].mean().round(2)
eng_compare.index = ["Retained", "Churned"]
eng_compare = eng_compare.T.reset_index()
eng_compare.rename(columns={"index": "Metric"}, inplace=True)

print(eng_compare.to_string(index=False))
eng_compare.to_csv(f"{PROCESSED}/engagement_comparison.csv", index=False)
print("  Saved → engagement_comparison.csv")


# =============================================================
# CHURN REASON ANALYSIS (from churn_events)
# =============================================================
print("\n[4] Churn reason analysis...")

churn_events = pd.read_csv("data/raw/ravenstack_churn_events.csv")
churn_events["reason_code"] = churn_events["reason_code"].str.lower().str.strip()

reason_summary = churn_events.groupby("reason_code").agg(
    Events          = ("churn_event_id",          "count"),
    AvgRefund       = ("refund_amount_usd",        "mean"),
    TotalRefund     = ("refund_amount_usd",        "sum"),
    Reactivations   = ("is_reactivation",          "sum"),
    PrecededByUpgrade   = ("preceding_upgrade_flag",   "sum"),
    PrecededByDowngrade = ("preceding_downgrade_flag", "sum"),
).reset_index().sort_values("Events", ascending=False)

reason_summary["AvgRefund"]   = reason_summary["AvgRefund"].round(2)
reason_summary["TotalRefund"] = reason_summary["TotalRefund"].round(2)

print(reason_summary.to_string(index=False))
reason_summary.to_csv(f"{PROCESSED}/churn_reason_summary.csv", index=False)
print("  Saved → churn_reason_summary.csv")


print("\n✓ Churn metrics complete.")