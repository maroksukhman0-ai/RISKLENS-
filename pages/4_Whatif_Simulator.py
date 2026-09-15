import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="What-If Simulator", layout="wide")

st.title("What-If Intervention Simulator")
st.write(
    "Simulate the impact of school-wide interventions — see how improving attendance "
    "or assignment submission across the class could shift the overall risk picture."
)

df = pd.read_csv("student_risk_dataset.csv")

df["AttendancePercent"] = df["AttendancePercent"].fillna(df["AttendancePercent"].median())
df["AssignmentSubmissionRate"] = df["AssignmentSubmissionRate"].fillna(df["AssignmentSubmissionRate"].median())
df["Avg_Score"] = df[["Test1_Score", "Test2_Score", "Test3_Score"]].mean(axis=1)
df["Trend"] = df["Test3_Score"] - df["Test1_Score"]
df["IsDeclining"] = df["Trend"] < -10

def calc_risk(attendance, assignment_rate, avg_score, is_declining):
    return (
        (100 - attendance) * 0.3
        + (100 - assignment_rate) * 0.25
        + (100 - avg_score) * 0.3
        + is_declining.astype(int) * 15
    )

def risk_level(score):
    return np.where(score > 60, "High Risk", np.where(score > 35, "Medium Risk", "Low Risk"))

df["RiskScore_Before"] = calc_risk(df["AttendancePercent"], df["AssignmentSubmissionRate"], df["Avg_Score"], df["IsDeclining"])
df["RiskLevel_Before"] = risk_level(df["RiskScore_Before"])

st.markdown("---")
st.subheader("Adjust the Intervention")

col1, col2 = st.columns(2)
with col1:
    attendance_boost = st.slider("Improve class-wide attendance by (%)", 0, 30, 10)
with col2:
    submission_boost = st.slider("Improve assignment submission by (%)", 0, 30, 10)

# Simulated "after" scenario
sim_attendance = (df["AttendancePercent"] + attendance_boost).clip(upper=100)
sim_submission = (df["AssignmentSubmissionRate"] + submission_boost).clip(upper=100)

df["RiskScore_After"] = calc_risk(sim_attendance, sim_submission, df["Avg_Score"], df["IsDeclining"])
df["RiskLevel_After"] = risk_level(df["RiskScore_After"])

st.markdown("---")

before_high = (df["RiskLevel_Before"] == "High Risk").sum()
after_high = (df["RiskLevel_After"] == "High Risk").sum()
saved = before_high - after_high

m1, m2, m3 = st.columns(3)
m1.metric("High Risk Students (Before)", int(before_high))
m2.metric("High Risk Students (After)", int(after_high), delta=int(after_high - before_high))
m3.metric("Students Moved Out of High Risk", int(saved))

col3, col4 = st.columns(2)

with col3:
    st.subheader("Before Intervention")
    fig1, ax1 = plt.subplots()
    df["RiskLevel_Before"].value_counts().reindex(["Low Risk", "Medium Risk", "High Risk"]).plot(
        kind="bar", ax=ax1, color=["green", "orange", "red"]
    )
    ax1.set_ylabel("Number of Students")
    st.pyplot(fig1)

with col4:
    st.subheader("After Intervention")
    fig2, ax2 = plt.subplots()
    df["RiskLevel_After"].value_counts().reindex(["Low Risk", "Medium Risk", "High Risk"]).plot(
        kind="bar", ax=ax2, color=["green", "orange", "red"]
    )
    ax2.set_ylabel("Number of Students")
    st.pyplot(fig2)

st.info(
    f"Boosting attendance by {attendance_boost}% and assignment submission by {submission_boost}% "
    f"across the class could move **{max(saved, 0)} students** out of the High Risk category, "
    "based on our scoring model."
)

st.markdown("---")

# -----------------------------
# LEADERBOARDS
# -----------------------------
st.subheader("Leaderboards")

lc1, lc2 = st.columns(2)

with lc1:
    st.write("**Most Improved Students** (Test1 to Test3)")
    improved = df.sort_values("Trend", ascending=False).head(5)[["Name", "Class", "Test1_Score", "Test3_Score", "Trend"]]
    st.dataframe(improved, hide_index=True)

with lc2:
    st.write("**Most Declined Students** (Test1 to Test3)")
    declined = df.sort_values("Trend", ascending=True).head(5)[["Name", "Class", "Test1_Score", "Test3_Score", "Trend"]]
    st.dataframe(declined, hide_index=True)

st.caption(
    "This simulator uses the same transparent, rule-based formula as the rest of the system — "
    "it shows the projected effect of intervention, not a guaranteed outcome."
)