# =============================================================
# 05_export_for_powerbi.py
# Final validation pass — confirms all Power BI files exist,
# prints row counts, column lists, and a load checklist.
# =============================================================

import pandas as pd
import os

PROCESSED = "data/processed"

# Files Power BI needs and what each is used for
POWERBI_FILES = {
    "master_accounts.csv"       : "Main table — all slicers, custom visuals, drill-through",
    "core_metrics.csv"          : "KPI cards (churn rate, retention rate, CLV, MRR lost)",
    "segment_summary.csv"       : "Bar charts — churn by plan, industry, tenure, engagement",
    "cohort_retention.csv"      : "Line/area chart — monthly retention trend",
    "cohort_by_quarter.csv"     : "Quarterly trend line",
    "churn_heatmap.csv"         : "Matrix visual — plan tier × tenure churn heatmap",
    "engagement_comparison.csv" : "Grouped bar — churned vs retained engagement metrics",
    "churn_reason_summary.csv"  : "Bar chart — why customers churn (reason codes)",
}

print("=" * 60)
print("POWER BI EXPORT CHECKLIST")
print("=" * 60)

all_good = True
for filename, purpose in POWERBI_FILES.items():
    filepath = os.path.join(PROCESSED, filename)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        print(f"\n✓ {filename}")
        print(f"    Rows: {len(df)}  |  Cols: {df.shape[1]}")
        print(f"    Use : {purpose}")
        print(f"    Cols: {', '.join(df.columns.tolist())}")
    else:
        print(f"\n✗ MISSING: {filename}")
        print(f"    Run the earlier scripts first.")
        all_good = False

print("\n" + "=" * 60)
if all_good:
    print("✓ All files ready. Load these CSVs into Power BI:")
    print(f"  Folder: {os.path.abspath(PROCESSED)}")
    print("""
POWER BI LOAD ORDER:
  1. master_accounts.csv        ← primary table
  2. core_metrics.csv           ← KPI cards
  3. segment_summary.csv        ← segment bar charts
  4. cohort_retention.csv       ← monthly cohort line chart
  5. cohort_by_quarter.csv      ← quarterly trend
  6. churn_heatmap.csv          ← matrix heatmap visual
  7. engagement_comparison.csv  ← engagement bar chart
  8. churn_reason_summary.csv   ← reason code bar chart

SUGGESTED DASHBOARD PAGES:
  Page 1 Executive Summary   : KPI cards + churn/retention overview
  Page 2 Segment Analysis    : churn by plan, industry, country, tenure
  Page 3 Cohort Retention    : monthly/quarterly trend + heatmap
  Page 4 Engagement & Usage  : engagement vs churn comparison
  Page 5 Churn Reasons       : reason codes + refunds + reactivation
""")
else:
    print("✗ Some files are missing. Run scripts 01 → 04 first.")