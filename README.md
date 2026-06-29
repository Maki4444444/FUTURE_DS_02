# Customer Churn Analysis & Retention Dashboard

## Overview

This project analyzes customer churn for a SaaS business using Python for data analysis and Power BI for interactive visualization. The objective is to identify the primary drivers of customer churn, measure its financial impact, and provide actionable recommendations to improve customer retention.

The project was completed as part of the **Future Interns Data Science Internship (Task 2).**


## Project Objectives

* Analyze customer churn patterns
* Identify key factors influencing customer retention
* Measure the financial impact of churn
* Build an interactive Power BI dashboard
* Provide business recommendations backed by data


## Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Power BI
* Jupyter Notebook


## Repository Structure


FUTURE_DS_02/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── exploration.ipynb
│
├── outputs/
│   └── dashboard
│   └── figures
│
├── docs/
│   ├── insights_summary.md
│   └── dashboard_screenshots/
│
├── scripts
│
├── requirements.txt
└── README.md


## Dashboard Highlights

The Power BI dashboard includes:

* Customer Churn Rate
* Monthly Recurring Revenue (MRR)
* Churned Revenue
* Customer Lifetime Value (CLV)
* Churn by Plan Tier
* Churn Reasons
* Customer Engagement Analysis
* Monthly Cohort Retention
* Interactive filters and drill-down analysis


## Key Findings

### 1. Churn Is a Product-Wide Issue

Enterprise, Pro, and Basic plans all experience nearly identical churn rates (~22%), suggesting retention challenges are driven by product experience rather than pricing.


### 2. Engagement Does Not Predict Churn

Highly engaged customers still leave the platform, indicating that feature gaps, competition, and business needs outweigh usage behavior.


### 3. Multiple Factors Drive Churn

Feature requests, support issues, budget limitations, pricing, and competitor offerings all contribute similarly to customer cancellations. No single issue explains most churn.


### 4. Newer Cohorts Show Better Retention

Customers acquired during late 2024 currently exhibit stronger retention, although additional observation is required to determine whether this trend is sustained.


### 5. Significant Revenue Lost to Churn

The business currently loses approximately:

* **$2.35M Monthly Recurring Revenue**
* **20.8% of Total MRR**

Reducing churn by even a small percentage could generate substantial recurring revenue.


## Business Recommendations

* Prioritize product improvements over pricing adjustments.
* Strengthen customer success initiatives.
* Improve exit survey completion to reduce unknown churn reasons.
* Create proactive win-back campaigns for budget-sensitive customers.
* Monitor cohort retention as customers reach renewal periods.


## Project Workflow

1. Data Cleaning
2. Exploratory Data Analysis (EDA)
3. Customer Segmentation
4. Cohort & Retention Analysis
5. Power BI Dashboard Development
6. Business Insight Generation
7. Strategic Recommendations

---

## Dashboard Preview

> screenshots of the power bi dashboard are found in outputs/ dashboard directory.


## Results

The analysis demonstrates that reducing churn requires a cross-functional strategy involving Product, Customer Success, Sales, and Support rather than isolated pricing or marketing initiatives.

The dashboard enables stakeholders to quickly identify retention risks, quantify revenue impact, and prioritize high-value improvement opportunities.

