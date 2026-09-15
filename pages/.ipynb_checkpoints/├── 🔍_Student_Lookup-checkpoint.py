import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Student Lookup", layout="wide")

st.title("Individual Student Lookup")
st.write("Search for a specific student to see their full risk profile and performance history.")

df = pd.read_csv("student_risk_dataset.csv")

df["AttendancePercent"] = df["AttendancePercent"].fillna(df["AttendancePercent"].median())
df["AssignmentSubmissionRate"] = df["AssignmentSubmissionRate"].fillna(df["AssignmentSubmissionRate"].median())

df["Avg_Score"] = df[["Test1_Score", "Test2_Score", "Test3_Score"]].mean(axis=1)
df["Trend"] = df["Test3_Score"] - df["Test1_Score"]
df["IsDeclining"] = df["Trend"] < -10

df["RiskScore"] = (
    (100 - df["AttendancePercent"]) * 0.3
    + (100 - df["AssignmentSubmissionRate"]) * 0.25
    + (100 - df["Avg_Score"]) * 0.3
    + df["IsDeclining"].astype(int) * 15
)

df["RiskLevel"] = np.where(
    df["RiskScore"] > 60, "High Risk",
    np.where(df["RiskScore"] > 35, "Medium Risk", "Low Risk")
)

st.markdown("---")

search_mode = st.radio("Search by", ["Student ID", "Name"], horizontal=True)

if search_mode == "Student ID":
    student_id = st.number_input("Enter Student ID", min_value=int(df["StudentID"].min()),
                                  max_value=int(df["StudentID"].max()), value=int(df["StudentID"].min()))
    match = df[df["StudentID"] == student_id]
else:
    name_query = st.text_input("Enter student name (or part of it)")
    match = df[df["Name"].str.contains(name_query, case=False, na=False)] if name_query else pd.DataFrame()

if search_mode == "Name" and len(match) > 1:
    st.write(f"Found {len(match)} matches — pick one:")
    chosen_name = st.selectbox("Select student", match["Name"].tolist())
    match = match[match["Name"] == chosen_name]

if len(match) == 0:
    st.info("Enter a valid Student ID or name to see their profile.")
else:
    row = match.iloc[0]

    st.markdown("---")
    st.subheader(f"{row['Name']}  |  Class {row['Class']}  |  Student ID {row['StudentID']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average Score", f"{row['Avg_Score']:.1f}")
    c2.metric("Attendance", f"{row['AttendancePercent']:.0f}%")
    c3.metric("Assignment Rate", f"{row['AssignmentSubmissionRate']:.0f}%")
    c4.metric("Risk Score", f"{row['RiskScore']:.1f}")

    if row["RiskLevel"] == "High Risk":
        st.error(f"Risk Level: {row['RiskLevel']}")
    elif row["RiskLevel"] == "Medium Risk":
        st.warning(f"Risk Level: {row['RiskLevel']}")
    else:
        st.success(f"Risk Level: {row['RiskLevel']}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Score Trend")
        fig, ax = plt.subplots()
        ax.plot(["Test1", "Test2", "Test3"],
                [row["Test1_Score"], row["Test2_Score"], row["Test3_Score"]],
                marker="o", color="blue")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 100)
        st.pyplot(fig)
        if row["IsDeclining"]:
            st.caption("Trend: declining across the three tests.")
        else:
            st.caption("Trend: stable or improving.")

    with col2:
        st.subheader("Risk Score Breakdown")
        breakdown = pd.Series({
            "Attendance factor": (100 - row["AttendancePercent"]) * 0.3,
            "Assignment factor": (100 - row["AssignmentSubmissionRate"]) * 0.25,
            "Score factor": (100 - row["Avg_Score"]) * 0.3,
            "Declining penalty": 15 if row["IsDeclining"] else 0,
        })
        fig2, ax2 = plt.subplots()
        breakdown.plot(kind="barh", ax=ax2, color="teal")
        ax2.set_xlabel("Points contributed to Risk Score")
        st.pyplot(fig2)

    st.markdown("---")
    st.subheader("Recommended Intervention")
    if row["RiskLevel"] == "High Risk":
        if row["AttendancePercent"] < 60:
            st.write("Immediate counselor meeting recommended — attendance is the primary concern.")
        elif row["IsDeclining"]:
            st.write("Academic support recommended — performance is actively declining.")
        else:
            st.write("General academic support recommended — multiple risk factors present.")
    elif row["RiskLevel"] == "Medium Risk":
        st.write("Monitor closely and encourage more consistent study habits and attendance.")
    else:
        st.write("Student is on track. No action needed at this time.")

    st.markdown("---")
    st.subheader("How this student compares to the class")
    class_avg_risk = df[df["Class"] == row["Class"]]["RiskScore"].mean()
    diff = row["RiskScore"] - class_avg_risk
    if diff > 0:
        st.write(f"This student's Risk Score is **{diff:.1f} points higher** than the Class {row['Class']} average.")
    else:
        st.write(f"This student's Risk Score is **{abs(diff):.1f} points lower** than the Class {row['Class']} average.")