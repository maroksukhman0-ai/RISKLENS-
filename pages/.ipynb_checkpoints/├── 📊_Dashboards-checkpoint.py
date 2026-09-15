import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Class Dashboards", layout="wide")

st.title("Class-Wide Risk Dashboards")
st.write("Explore attendance, performance trends and risk patterns across the whole dataset.")

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

st.sidebar.header("Filters")
class_options = sorted(df["Class"].unique())
selected_classes = st.sidebar.multiselect("Class", options=class_options, default=class_options)
df_filtered = df[df["Class"].isin(selected_classes)]

st.sidebar.markdown("---")
st.sidebar.write(f"Showing **{len(df_filtered)}** students")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Students", len(df_filtered))
m2.metric("High Risk", int((df_filtered["RiskLevel"] == "High Risk").sum()))
m3.metric("Declining Students", int(df_filtered["IsDeclining"].sum()))
m4.metric("Avg Attendance", f"{df_filtered['AttendancePercent'].mean():.1f}%")

st.markdown("---")

if st.checkbox("Show raw data"):
    st.dataframe(df_filtered)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Risk Level Distribution")
    fig1, ax1 = plt.subplots()
    df_filtered["RiskLevel"].value_counts().plot(kind="bar", ax=ax1, color=["green", "orange", "red"])
    ax1.set_xlabel("Risk Level")
    ax1.set_ylabel("Number of Students")
    st.pyplot(fig1)

with col2:
    st.subheader("Attendance vs Risk Score")
    fig2, ax2 = plt.subplots()
    ax2.scatter(df_filtered["AttendancePercent"], df_filtered["RiskScore"], alpha=0.5)
    ax2.set_xlabel("Attendance %")
    ax2.set_ylabel("Risk Score")
    st.pyplot(fig2)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Declining vs Stable Students")
    fig3, ax3 = plt.subplots()
    df_filtered["IsDeclining"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax3, colors=["lightgreen", "salmon"],shadow = True)
    ax3.set_ylabel("")
    st.pyplot(fig3)

with col4:
    st.subheader("Average Risk Score by Class")
    fig4, ax4 = plt.subplots()
    df_filtered.groupby("Class")["RiskScore"].mean().plot(kind="bar", ax=ax4, color="skyblue")
    ax4.set_xlabel("Class")
    ax4.set_ylabel("Average Risk Score")
    st.pyplot(fig4)

st.markdown("---")

st.subheader("Score Trend — Sample Declining Students")
declining_students = df_filtered[df_filtered["IsDeclining"] == True].head(5)

if len(declining_students) == 0:
    st.write("No declining students in the current selection.")
else:
    fig5, ax5 = plt.subplots()
    for idx, row in declining_students.iterrows():
        ax5.plot(["Test1", "Test2", "Test3"],
                 [row["Test1_Score"], row["Test2_Score"], row["Test3_Score"]],
                 marker="o", label=row["Name"])
    ax5.set_xlabel("Test")
    ax5.set_ylabel("Score")
    ax5.legend()
    st.pyplot(fig5)

st.markdown("---")

def get_intervention(row):
    if row['RiskLevel'] == 'High Risk':
        if row['AttendancePercent'] < 60:
            return "Counselor meeting — attendance issue"
        elif row['IsDeclining']:
            return "Academic support — declining performance"
        else:
            return "General academic support"
    elif row['RiskLevel'] == 'Medium Risk':
        return "Monitor closely"
    else:
        return "On track"

df_filtered['Intervention'] = df_filtered.apply(get_intervention, axis=1)

st.subheader("Students Needing Attention")
high_risk = df_filtered[df_filtered["RiskLevel"] == "High Risk"][
    ["StudentID", "Class", "RiskScore", "AttendancePercent", "Avg_Score", "Intervention"]
].sort_values("RiskScore", ascending=False)

st.dataframe(high_risk)


st.download_button("Download High Risk List (CSV)", high_risk.to_csv(index=False), "high_risk_students.csv")

st.markdown("---")
st.subheader("Key Insights")

corr_attendance = df_filtered["AttendancePercent"].corr(df_filtered["RiskScore"])
pass_rate = (df_filtered["Avg_Score"] >= 40).mean() * 100

st.write(f"- Attendance shows a correlation of **{corr_attendance:.2f}** with Risk Score.")
st.write(f"- **{(df_filtered['RiskLevel'] == 'High Risk').mean() * 100:.1f}%** of students fall in the High Risk category.")
st.write(f"- **{df_filtered['IsDeclining'].mean() * 100:.1f}%** of students show a declining performance trend.")
st.write(f"- Overall pass rate (Average >= 40): **{pass_rate:.1f}%**")