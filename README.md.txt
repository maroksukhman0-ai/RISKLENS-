# 🎯 Risk Lens — Student Early Warning System

A transparent, rule-based early warning system that helps teachers and institutions identify at-risk students before performance decline becomes irreversible — built for the **Smart Education** theme.

## Problem Statement

Schools often identify academically struggling or disengaged students only after their performance has significantly declined. Attendance, assessment scores, and assignment data are usually available but rarely analyzed together to flag students who need timely intervention.

## What Risk Lens Does

- Analyzes attendance, test scores (across multiple checkpoints), and assignment submission rates
- Detects declining performance trends automatically
- Generates a transparent, explainable **Risk Score** for every student
- Classifies students into Low / Medium / High Risk
- Recommends specific interventions based on the root cause of risk
- Lets teachers search and view any individual student's full risk profile
- Simulates the impact of school-wide interventions (What-If Simulator)

## Live Demo

*(Add your Streamlit Cloud link here once deployed — see instructions below)*

## Screenshots

*(Add 2-3 screenshots of your app here once you have them — see instructions below)*

## Tech Stack

- Python
- Pandas & NumPy — data cleaning, feature engineering, risk scoring
- Matplotlib — visualizations
- Streamlit — interactive multi-page web app

## Project Structure
HACATHON_PROJECT/
├── app.py # Home page — upload data, overview
├── pages/
│ ├── 1_Dashboards.py # Class-wide visual dashboards
│ ├── 2_Student_Lookup.py # Individual student search & profile
│ └── 3_Whatif_Simulator.py # Intervention impact simulator
├── student_risk_dataset.csv # Sample dataset
├── analysis_notebook.ipynb # Backend EDA & logic development
├── requirements.txt
└── README.md

## How It Works (Risk Score Formula)

A weighted, fully explainable formula — not a black-box model:
RiskScore = (100 - Attendance%) × 0.3
+ (100 - AssignmentSubmissionRate%) × 0.25
+ (100 - AverageScore) × 0.3
+ (15 if declining trend detected else 0)

Students are classified as:
- **High Risk:** Score > 60
- **Medium Risk:** Score 35–60
- **Low Risk:** Score < 35

## Running Locally

```bash
git clone https://github.com/YOUR_USERNAME/risk-lens.git
cd risk-lens
pip install -r requirements.txt
streamlit run app.py
```

## Key Findings (from sample dataset)

- Attendance shows a moderate negative correlation with Risk Score
- Students with declining test trends were reliably flagged as High Risk
- Rule-based scoring keeps the system fully explainable — teachers can see exactly why a student was flagged

## Team

**Future Coders** — NQ 4.O, ID 32

## Future Improvements

- Validate risk weights against real institutional data
- Deploy with authentication for multi-school use
- Explore a supervised ML upgrade once labeled historical outcomes are available