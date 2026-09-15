import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="RISKLENS -> Student Risk Detection System", layout="wide")

st.title("Student Early Warning & Risk Detection System")
st.write(
    "A data-driven early warning tool for Smart Education. "
    "Enter a student's details below to get an instant risk assessment, "
    "or open the **Dashboards** page (left sidebar) to explore patterns across the whole class."
)

st.markdown("---")

st.header("Check a Student's Risk")

col1, col2, col3 = st.columns(3)

with col1:
    attendance = st.number_input("Attendance %", min_value=0, max_value=100, value=75)
    study_hours = st.number_input("Study Hours Per Day", min_value=0.0, max_value=12.0, value=3.0, step=0.5)

with col2:
    assignment_rate = st.number_input("Assignment Submission Rate %", min_value=0, max_value=100, value=80)
    screen_time = st.number_input("Screen Time (hours/day)", min_value=0.0, max_value=15.0, value=3.0, step=0.5)

with col3:
    test1 = st.number_input("Test 1 Score", min_value=0, max_value=100, value=60)
    test2 = st.number_input("Test 2 Score", min_value=0, max_value=100, value=55)
    test3 = st.number_input("Test 3 Score", min_value=0, max_value=100, value=50)

if st.button("Get Risk Assessment", type="primary"):

    avg_score = (test1 + test2 + test3) / 3
    trend = test3 - test1
    is_declining = trend < -10

    risk_score = (
        (100 - attendance) * 0.3 +
        (100 - assignment_rate) * 0.25 +
        (100 - avg_score) * 0.3 +
        (15 if is_declining else 0)
    )
    risk_score = round(risk_score, 1)

    if risk_score > 60:
        risk_level = "High Risk"
    elif risk_score > 35:
        risk_level = "Medium Risk"
    else:
        risk_level = "Low Risk"

    st.markdown("### Result")

    r1, r2, r3 = st.columns(3)
    r1.metric("Average Score", f"{avg_score:.1f}")
    r2.metric("Score Trend (Test1 to Test3)", f"{trend:+.0f}")
    r3.metric("Risk Score", f"{risk_score}")

    if risk_level == "High Risk":
        st.error(f"Risk Level: {risk_level}")
    elif risk_level == "Medium Risk":
        st.warning(f"Risk Level: {risk_level}")
    else:
        st.success(f"Risk Level: {risk_level}")

    st.markdown("### Recommended Intervention")

    if risk_level == "High Risk":
        if attendance < 60:
            st.write("Immediate counselor meeting recommended — attendance is the primary concern.")
        elif is_declining:
            st.write("Academic support recommended — performance is actively declining across tests.")
        else:
            st.write("General academic support recommended — multiple risk factors present.")
    elif risk_level == "Medium Risk":
        st.write("Monitor closely and encourage more consistent study habits and attendance.")
    else:
        st.write("Student is on track. No action needed at this time.")

    st.markdown("### Why this score?")
    st.write(f"- Attendance contributed **{(100 - attendance) * 0.3:.1f}** points")
    st.write(f"- Assignment submission contributed **{(100 - assignment_rate) * 0.25:.1f}** points")
    st.write(f"- Average score contributed **{(100 - avg_score) * 0.3:.1f}** points")
    st.write(f"- Declining trend penalty: **{15 if is_declining else 0}** points")
    st.caption(
        "This is a transparent, rule-based score (not a trained ML model) — "
        "every point is traceable to a specific factor, so the reasoning is always explainable."
    )
else:
    st.info("Enter a student's details above and click **Get Risk Assessment** to see the result.")
