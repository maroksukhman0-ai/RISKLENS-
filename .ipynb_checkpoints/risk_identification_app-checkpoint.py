
import numpy as np
import pandas as pd
import streamlit as st
from utils import inject_css, page_header, metric_card, get_data, RISK_COLORS


# ----------------------------------------------------------------------
# THEME / CONSTANTS
# ----------------------------------------------------------------------

RISK_COLORS = {"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"}
RISK_ORDER = ["Low", "Medium", "High"]

PRIMARY = "#4f46e5"
PRIMARY_DARK = "#3730a3"
BG_CARD = "#ffffff"


def inject_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(180deg, #f7f8fc 0%, #eef1fb 100%);
        }}
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {PRIMARY_DARK} 0%, {PRIMARY} 100%);
        }}
        section[data-testid="stSidebar"] * {{
            color: #f5f5ff !important;
        }}
        .app-header {{
            padding: 1.4rem 1.8rem;
            border-radius: 16px;
            background: linear-gradient(120deg, {PRIMARY_DARK}, {PRIMARY});
            color: white;
            margin-bottom: 1.4rem;
            box-shadow: 0 8px 24px rgba(79,70,229,0.25);
        }}
        .app-header h1 {{
            margin: 0;
            font-size: 1.7rem;
            font-weight: 700;
        }}
        .app-header p {{
            margin: 0.3rem 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }}
        .metric-card {{
            background: {BG_CARD};
            border-radius: 14px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 2px 10px rgba(30,30,60,0.06);
            border: 1px solid rgba(79,70,229,0.08);
        }}
        .metric-card .label {{
            font-size: 0.8rem;
            color: #6b7280;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .metric-card .value {{
            font-size: 1.8rem;
            font-weight: 800;
            color: #1f2937;
            margin-top: 0.15rem;
        }}
        .badge {{
            display: inline-block;
            padding: 0.35rem 0.9rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.95rem;
            color: white;
        }}
        .section-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #1f2937;
            margin: 1.2rem 0 0.6rem 0;
            border-left: 5px solid {PRIMARY};
            padding-left: 0.6rem;
        }}
        .factor-row {{
            padding: 0.5rem 0.8rem;
            border-radius: 10px;
            background: #f9fafb;
            margin-bottom: 0.4rem;
            border-left: 4px solid {PRIMARY};
            font-size: 0.92rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle=""):
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, col):
    col.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(level):
    color = RISK_COLORS.get(level, "#6b7280")
    return f'<span class="badge" style="background:{color};">{level} Risk</span>'


# ----------------------------------------------------------------------
# RULE-BASED RISK ENGINE
# ----------------------------------------------------------------------
# The score is built from transparent, explainable rules (not a black-box
# model) so a teacher/counsellor can see exactly why a student was flagged.
#
#   Component                 Max points   Trigger
#   ------------------------  -----------  -----------------------------
#   Low attendance             ~35 pts     attendance below 85%
#   Weak academics              ~25 pts     average score below 60
#   Declining score trend       20 pts     negative slope across tests
#   Fee dues pending              6 pts     flag
#   Disciplinary record           6 pts     flag
#   Low participation            up to 8    participation score below 5
#   Good participation         -up to 7.5   participation score above 5 (relief)
#
# Final score is clipped to 0-100.
#   0  - 29.9  -> Low risk
#   30 - 59.9  -> Medium risk
#   60 - 100   -> High risk


def compute_trend_slope(scores):
    """Least-squares slope across a sequence of test scores."""
    scores = [s for s in scores if s is not None]
    if len(scores) < 2:
        return 0.0
    x = np.arange(len(scores))
    slope = np.polyfit(x, scores, 1)[0]
    return float(slope)


def calculate_risk_score(attendance, avg_score, trend_slope, fee_pending=False,
                          disciplinary=False, participation=5):
    """Rule-based additive risk score, 0-100 (higher = more at-risk)."""
    risk = 0.0
    breakdown = {}

    attendance_pts = max(0.0, (90 - attendance)) * 0.75
    risk += attendance_pts
    breakdown["Low attendance"] = round(attendance_pts, 1)

    academic_pts = max(0.0, (64 - avg_score)) * 0.62
    risk += academic_pts
    breakdown["Weak academic average"] = round(academic_pts, 1)

    trend_pts = min(abs(trend_slope) * 4.5, 20) if trend_slope < 0 else 0.0
    risk += trend_pts
    breakdown["Declining score trend"] = round(trend_pts, 1)

    fee_pts = 5.0 if fee_pending else 0.0
    risk += fee_pts
    breakdown["Fee dues pending"] = fee_pts

    disc_pts = 5.0 if disciplinary else 0.0
    risk += disc_pts
    breakdown["Disciplinary record"] = disc_pts

    participation_pts = max(0.0, (5 - participation)) * 1.4
    risk += participation_pts
    breakdown["Low participation"] = round(participation_pts, 1)

    relief = max(0.0, (participation - 5)) * 1.3
    risk -= relief
    breakdown["Participation relief (reduces risk)"] = -round(relief, 1)

    risk = float(np.clip(risk, 0, 100))
    return round(risk, 1), breakdown


def get_risk_level(score):
    if score < 30:
        return "Low"
    elif score < 60:
        return "Medium"
    return "High"


def recommendations_for(level, breakdown, attendance, avg_score, trend_slope):
    recs = []
    if attendance < 75:
        recs.append("Schedule a parent-teacher meeting to address irregular attendance.")
    if avg_score < 50:
        recs.append("Enroll the student in remedial classes or peer tutoring for weak subjects.")
    if trend_slope < -3:
        recs.append("Flag for close academic monitoring — scores are dropping fast across recent tests.")
    if breakdown.get("Fee dues pending", 0) > 0:
        recs.append("Coordinate with administration on fee dues — financial stress is a common dropout driver.")
    if breakdown.get("Disciplinary record", 0) > 0:
        recs.append("Involve the school counsellor to address behavioural/disciplinary concerns.")
    if breakdown.get("Low participation", 0) > 0:
        recs.append("Encourage participation in class activities, clubs, or mentorship programs.")
    if level == "Low" and not recs:
        recs.append("No major risk factors detected — continue routine monitoring.")
    if level == "High":
        recs.insert(0, "Immediate counsellor intervention recommended — this student is at high dropout risk.")
    return recs


# ----------------------------------------------------------------------
# SAMPLE DATA GENERATOR
# ----------------------------------------------------------------------

FIRST_NAMES = [
    "Karan", "Divya", "Neha", "Sneha", "Ishita", "Aarav", "Priya", "Rohan",
    "Ananya", "Vikram", "Simran", "Aditya", "Pooja", "Rahul", "Kavya",
    "Arjun", "Meera", "Sahil", "Riya", "Yash", "Tanvi", "Devansh", "Nisha",
    "Manav", "Aisha", "Kabir", "Shreya", "Harsh", "Diya", "Aryan",
]
LAST_NAMES = [
    "Mehta", "Chatterjee", "Singh", "Kapoor", "Verma", "Sharma", "Gupta",
    "Reddy", "Nair", "Iyer", "Khanna", "Malhotra", "Chauhan", "Bhatia",
    "Joshi", "Rao", "Desai", "Kaur", "Agarwal", "Bose",
]


@st.cache_data(show_spinner=False)
def generate_sample_data(n=500, seed=7):
    rng = np.random.default_rng(seed)

    classes = rng.choice(["10th", "11th", "12th"], size=n, p=[0.36, 0.34, 0.30])
    # 10th students get a mild negative bias on attendance to reproduce the
    # "avg risk score by class" pattern (10th slightly higher risk).
    class_bias = np.where(classes == "10th", -6, np.where(classes == "11th", -2, 0))

    attendance = np.clip(rng.normal(75, 16, n) + class_bias, 35, 100)

    is_declining = rng.random(n) < 0.21  # ~21% declining, matches pie chart

    test1 = np.clip(rng.normal(58, 16, n), 3, 100)
    test2 = np.where(
        is_declining,
        np.clip(test1 - rng.uniform(4, 18, n), 0, 100),
        np.clip(test1 + rng.normal(0, 4, n), 0, 100),
    )
    test3 = np.where(
        is_declining,
        np.clip(test2 - rng.uniform(4, 18, n), 0, 100),
        np.clip(test2 + rng.normal(0, 4, n), 0, 100),
    )

    avg_score = (test1 + test2 + test3) / 3
    fee_pending = rng.random(n) < 0.15
    disciplinary = rng.random(n) < 0.08
    participation = rng.integers(1, 11, n)

    trend_slope = np.array([
        compute_trend_slope([test1[i], test2[i], test3[i]]) for i in range(n)
    ])

    risk_scores = []
    for i in range(n):
        score, _ = calculate_risk_score(
            attendance[i], avg_score[i], trend_slope[i],
            fee_pending[i], disciplinary[i], participation[i],
        )
        risk_scores.append(score)
    risk_scores = np.array(risk_scores)
    risk_levels = [get_risk_level(s) for s in risk_scores]

    names = [f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}" for _ in range(n)]

    df = pd.DataFrame({
        "student_id": [f"STU{1000+i}" for i in range(n)],
        "name": names,
        "class": classes,
        "attendance_percent": np.round(attendance, 1),
        "test1": np.round(test1, 1),
        "test2": np.round(test2, 1),
        "test3": np.round(test3, 1),
        "avg_score": np.round(avg_score, 1),
        "score_trend": np.where(is_declining, "Declining", "Stable"),
        "trend_slope": np.round(trend_slope, 2),
        "fee_pending": fee_pending,
        "disciplinary_issues": disciplinary,
        "participation_score": participation,
        "risk_score": risk_scores,
        "risk_level": risk_levels,
    })
    return df


def get_data():
    """Returns the active working dataset (uploaded or sample), shared across pages."""
    if "student_df" not in st.session_state:
        st.session_state["student_df"] = generate_sample_data()
        st.session_state["data_source"] = "Sample (synthetic) dataset"
    return st.session_state["student_df"]


def set_data(df, source_label):
    st.session_state["student_df"] = df
    st.session_state["data_source"] = source_label
    import streamlit as st
from utils import inject_css, page_header, metric_card, get_data, RISK_COLORS

st.set_page_config(
    page_title="Student Dropout & Risk Detection System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

page_header(
    "🎓 Student Dropout & Risk Detection System",
    "A rule-based early-warning system for identifying at-risk students — transparent, explainable, and built for educators.",
)

df = get_data()

st.markdown('<div class="section-title">Snapshot of Current Data</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
metric_card("Total Students", f"{len(df):,}", c1)
metric_card("Average Risk Score", f"{df['risk_score'].mean():.1f}", c2)
metric_card("High Risk Students", f"{(df['risk_level']=='High').sum():,}", c3)
metric_card("Declining Trend", f"{(df['score_trend']=='Declining').sum():,}", c4)

st.caption(f"Data source: *{st.session_state.get('data_source', 'Sample dataset')}* — "
           "switch or upload your own on the Student Database page.")

st.markdown("---")

left, right = st.columns([1.3, 1])

with left:
    st.markdown('<div class="section-title">How this system works</div>', unsafe_allow_html=True)
    st.markdown(
        """
        This app uses a *rule-based risk engine* — not a black-box ML model — so every
        prediction can be explained to a teacher, parent, or administrator in plain language.

        The risk score (0–100) is built additively from weighted factors:

        - 📉 *Attendance below 85%* — the single strongest driver of risk
        - 📚 *Weak academic average* (below 60)
        - 📈 *Declining score trend* across recent tests
        - 💰 *Pending fee dues*
        - ⚠️ *Disciplinary record*
        - 🙋 *Low class participation* (participation reduces risk when high)

        Students are then bucketed into *Low / Medium / High* risk, matching the same
        thresholds used throughout the dashboard.
        """
    )

with right:
    st.markdown('<div class="section-title">Explore the app</div>', unsafe_allow_html=True)
    st.markdown(
        """
        *📊 Dashboard* — Interactive charts: attendance vs. risk, score trends,
        declining vs. stable students, risk by class, and overall risk distribution.

        *🔍 Risk Checker* — Enter a single student's details and get an instant
        risk verdict with a full explanation and recommended actions.

        *🗂️ Student Database* — Browse, filter, search, upload your own CSV,
        and export the working dataset.
        """
    )
    st.info("Use the sidebar to navigate between pages.", icon="👈")

st.markdown("---")
st.markdown(
    '<div class="section-title">Risk Level Legend</div>',
    unsafe_allow_html=True,
)
l1, l2, l3 = st.columns(3)
for col, level, desc in zip(
    [l1, l2, l3],
    ["Low", "Medium", "High"],
    ["Score 0–29 · routine monitoring", "Score 30–59 · needs attention", "Score 60–100 · immediate intervention"],
):
    col.markdown(
        f"""
        <div class="metric-card" style="border-top:5px solid {RISK_COLORS[level]};">
            <div class="label">{level.upper()} RISK</div>
            <div style="color:#4b5563; margin-top:0.3rem; font-size:0.9rem;">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils import inject_css, page_header, metric_card, get_data, RISK_COLORS

st.set_page_config(page_title="Dashboard | Risk Detection System", page_icon="📊", layout="wide")
inject_css()
page_header("📊 Risk Analytics Dashboard", "Live, filterable visual analysis of the current student dataset.")

df = get_data()

# ---------------- Sidebar filters ----------------
st.sidebar.header("🔎 Filters")
classes = st.sidebar.multiselect("Class", sorted(df["class"].unique()), default=sorted(df["class"].unique()))
risk_levels = st.sidebar.multiselect("Risk Level", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])
att_range = st.sidebar.slider("Attendance % range", 0, 100, (0, 100))

fdf = df[
    df["class"].isin(classes)
    & df["risk_level"].isin(risk_levels)
    & df["attendance_percent"].between(att_range[0], att_range[1])
]

if fdf.empty:
    st.warning("No students match the selected filters.")
    st.stop()

# ---------------- KPI row ----------------
c1, c2, c3, c4 = st.columns(4)
metric_card("Students (filtered)", f"{len(fdf):,}", c1)
metric_card("Avg. Risk Score", f"{fdf['risk_score'].mean():.1f}", c2)
metric_card("% High Risk", f"{(fdf['risk_level']=='High').mean()*100:.1f}%", c3)
metric_card("% Declining", f"{(fdf['score_trend']=='Declining').mean()*100:.1f}%", c4)

st.markdown("---")

# ---------------- Row 1: Attendance vs Risk + Risk Distribution ----------------
r1c1, r1c2 = st.columns([1.3, 1])

with r1c1:
    st.markdown('<div class="section-title">Attendance vs Risk Score</div>', unsafe_allow_html=True)
    fig = px.scatter(
        fdf, x="attendance_percent", y="risk_score", color="risk_level",
        color_discrete_map=RISK_COLORS,
        hover_data=["name", "class", "avg_score"],
        labels={"attendance_percent": "Attendance Percent", "risk_score": "Risk Score", "risk_level": "Risk Level"},
    )
    fig.update_traces(marker=dict(size=9, opacity=0.75, line=dict(width=0.5, color="white")))
    fig.update_layout(height=420, margin=dict(t=10, l=0, r=0, b=0), legend_title_text="Risk Level",
                       plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)
    counts = fdf["risk_level"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0)
    fig2 = go.Figure(go.Bar(
        x=counts.index, y=counts.values,
        marker_color=[RISK_COLORS[l] for l in counts.index],
        text=counts.values.astype(int), textposition="outside",
    ))
    fig2.update_layout(height=420, margin=dict(t=10, l=0, r=0, b=0),
                        yaxis_title="Number of Students", xaxis_title="Risk Level",
                        plot_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- Row 2: Declining vs Stable pie + Avg risk by class ----------------
r2c1, r2c2 = st.columns(2)

with r2c1:
    st.markdown('<div class="section-title">Declining vs Stable Students</div>', unsafe_allow_html=True)
    trend_counts = fdf["score_trend"].value_counts()
    fig3 = px.pie(
        values=trend_counts.values, names=trend_counts.index,
        color=trend_counts.index,
        color_discrete_map={"Stable": "#90ee90", "Declining": "#f88379"},
        hole=0.0,
    )
    fig3.update_traces(textinfo="percent+label", pull=[0.03] * len(trend_counts))
    fig3.update_layout(height=380, margin=dict(t=10, l=0, r=0, b=0), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with r2c2:
    st.markdown('<div class="section-title">Average Risk Score by Class</div>', unsafe_allow_html=True)
    by_class = fdf.groupby("class", as_index=False)["risk_score"].mean().sort_values("class")
    order = {"10th": 0, "11th": 1, "12th": 2}
    by_class["ord"] = by_class["class"].map(order)
    by_class = by_class.sort_values("ord")
    fig4 = go.Figure(go.Bar(
        x=by_class["class"], y=by_class["risk_score"],
        marker_color="#87CEEB", text=by_class["risk_score"].round(1), textposition="outside",
    ))
    fig4.update_layout(height=380, margin=dict(t=10, l=0, r=0, b=0),
                        yaxis_title="Average Risk Score", xaxis_title="Class", plot_bgcolor="white")
    st.plotly_chart(fig4, use_container_width=True)

# ---------------- Row 3: Score trend for top declining students ----------------
st.markdown('<div class="section-title">Score Trend — Sample Declining Students</div>', unsafe_allow_html=True)
declining = fdf[fdf["score_trend"] == "Declining"].sort_values("trend_slope").head(5)

if declining.empty:
    st.caption("No declining students in the current filter selection.")
else:
    fig5 = go.Figure()
    for _, row in declining.iterrows():
        fig5.add_trace(go.Scatter(
            x=["Test1", "Test2", "Test3"], y=[row["test1"], row["test2"], row["test3"]],
            mode="lines+markers", name=row["name"], marker=dict(size=8),
        ))
    fig5.update_layout(height=420, margin=dict(t=10, l=0, r=0, b=0),
                        yaxis_title="Score", xaxis_title="Test", plot_bgcolor="white",
                        legend_title_text="Student")
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.caption(
    "Tip: use the sidebar filters to slice the dashboard by class, risk level, and attendance range. "
    "All charts update together."
)
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils import (
    inject_css, page_header, calculate_risk_score, get_risk_level,
    compute_trend_slope, recommendations_for, risk_badge, RISK_COLORS, get_data,
)

st.set_page_config(page_title="Risk Checker | Risk Detection System", page_icon="🔍", layout="wide")
inject_css()
page_header("🔍 Student Risk Checker", "Enter a student's details below to get an instant, explainable risk assessment.")

left, right = st.columns([1, 1.1])

with left:
    st.markdown('<div class="section-title">Student Details</div>', unsafe_allow_html=True)
    with st.form("risk_form"):
        name = st.text_input("Student Name", placeholder="e.g. Ananya Sharma")
        student_class = st.selectbox("Class", ["10th", "11th", "12th"])
        attendance = st.slider("Attendance Percent", 0, 100, 80)

        st.markdown("*Recent Test Scores* (used to detect a declining trend)")
        t1, t2, t3 = st.columns(3)
        test1 = t1.number_input("Test 1", 0, 100, 60)
        test2 = t2.number_input("Test 2", 0, 100, 58)
        test3 = t3.number_input("Test 3", 0, 100, 55)

        c1, c2 = st.columns(2)
        fee_pending = c1.selectbox("Fee Dues Pending?", ["No", "Yes"]) == "Yes"
        disciplinary = c2.selectbox("Disciplinary Record?", ["No", "Yes"]) == "Yes"

        participation = st.slider(
            "Class Participation Score (1 = very low, 10 = very high)", 1, 10, 5
        )

        add_to_db = st.checkbox("Add this student to the Student Database after checking", value=False)
        submitted = st.form_submit_button("🚦 Check Risk", use_container_width=True)

with right:
    st.markdown('<div class="section-title">Result</div>', unsafe_allow_html=True)

    if not submitted:
        st.info("Fill in the form on the left and click *Check Risk* to see the assessment here.", icon="📝")
    else:
        avg_score = (test1 + test2 + test3) / 3
        trend_slope = compute_trend_slope([test1, test2, test3])
        risk_score, breakdown = calculate_risk_score(
            attendance, avg_score, trend_slope, fee_pending, disciplinary, participation
        )
        level = get_risk_level(risk_score)
        trend_label = "Declining" if trend_slope < 0 else "Stable"

        st.markdown(
            f"""
            <div class="metric-card" style="text-align:center;">
                <div class="label">{name if name else 'This student'} is classified as</div>
                <div style="margin-top:0.4rem;">{risk_badge(level)}</div>
                <div style="font-size:2.2rem; font-weight:800; margin-top:0.5rem; color:#1f2937;">
                    {risk_score} / 100
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            number={"suffix": " / 100"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": RISK_COLORS[level]},
                "steps": [
                    {"range": [0, 30], "color": "#dcfce7"},
                    {"range": [30, 60], "color": "#fef3c7"},
                    {"range": [60, 100], "color": "#fee2e2"},
                ],
            },
        ))
        gauge.update_layout(height=260, margin=dict(t=20, b=10, l=20, r=20))
        st.plotly_chart(gauge, use_container_width=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Average Score", f"{avg_score:.1f}")
        m2.metric("Score Trend", trend_label, delta=f"{trend_slope:.1f} pts/test")
        m3.metric("Attendance", f"{attendance}%")

        st.markdown('<div class="section-title">Why this score?</div>', unsafe_allow_html=True)
        for factor, pts in breakdown.items():
            if pts == 0:
                continue
            sign = "+" if pts > 0 else ""
            st.markdown(
                f'<div class="factor-row"><b>{factor}</b>: {sign}{pts} pts</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title">Recommended Actions</div>', unsafe_allow_html=True)
        for rec in recommendations_for(level, breakdown, attendance, avg_score, trend_slope):
            st.markdown(f"- {rec}")

        if add_to_db:
            df = get_data()
            new_id = f"STU{1000 + len(df) + 1}"
            new_row = pd.DataFrame([{
                "student_id": new_id,
                "name": name if name else new_id,
                "class": student_class,
                "attendance_percent": attendance,
                "test1": test1, "test2": test2, "test3": test3,
                "avg_score": round(avg_score, 1),
                "score_trend": trend_label,
                "trend_slope": round(trend_slope, 2),
                "fee_pending": fee_pending,
                "disciplinary_issues": disciplinary,
                "participation_score": participation,
                "risk_score": risk_score,
                "risk_level": level,
            }])
            st.session_state["student_df"] = pd.concat([df, new_row], ignore_index=True)
            st.success(f"Added {new_row['name'].iloc[0]} to the Student Database ✅ "
                       "View it on the Student Database page.")

st.markdown("---")
st.caption(
    "This tool applies transparent rules, not a predictive machine-learning model — "
    "it is meant to support, not replace, a teacher's or counsellor's judgement."
)
import streamlit as st
import pandas as pd

from utils import inject_css, page_header, metric_card, get_data, set_data, risk_badge, generate_sample_data

st.set_page_config(page_title="Student Database | Risk Detection System", page_icon="🗂️", layout="wide")
inject_css()
page_header("🗂️ Student Database", "Browse, search, filter, upload, and export the working dataset.")

# ---------------- Upload / reset controls ----------------
st.markdown('<div class="section-title">Data Source</div>', unsafe_allow_html=True)
u1, u2 = st.columns([2, 1])

with u1:
    uploaded = st.file_uploader(
        "Upload your own student CSV (expects columns similar to the sample dataset)",
        type=["csv"],
    )
    if uploaded is not None:
        try:
            new_df = pd.read_csv(uploaded)
            required = {"attendance_percent", "avg_score"}
            if not required.issubset(set(c.lower() for c in new_df.columns)):
                st.warning(
                    "This CSV doesn't look like it has the expected columns "
                    "(e.g. attendance_percent, avg_score). It was loaded anyway — "
                    "recompute risk scores manually if needed."
                )
            set_data(new_df, f"Uploaded file: {uploaded.name}")
            st.success(f"Loaded {len(new_df):,} rows from {uploaded.name}")
        except Exception as e:
            st.error(f"Couldn't read that file: {e}")

with u2:
    st.write("")
    st.write("")
    if st.button("↩️ Reset to sample dataset", use_container_width=True):
        set_data(generate_sample_data(), "Sample (synthetic) dataset")
        st.rerun()

df = get_data()
st.caption(f"Current source: *{st.session_state.get('data_source', 'Sample dataset')}* · {len(df):,} students loaded")

st.markdown("---")

# ---------------- Filters ----------------
st.markdown('<div class="section-title">Search & Filter</div>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns([1.4, 1, 1, 1])

search = f1.text_input("Search by name or student ID")
class_opts = sorted(df["class"].dropna().unique()) if "class" in df.columns else []
class_filter = f2.multiselect("Class", class_opts, default=class_opts)
risk_opts = ["Low", "Medium", "High"]
risk_filter = f3.multiselect(
    "Risk Level", [r for r in risk_opts if "risk_level" in df.columns and r in df["risk_level"].unique()] or risk_opts,
    default=None,
)
min_att, max_att = f4.slider("Attendance % range", 0, 100, (0, 100))

fdf = df.copy()
if search:
    mask = pd.Series(False, index=fdf.index)
    if "name" in fdf.columns:
        mask |= fdf["name"].astype(str).str.contains(search, case=False, na=False)
    if "student_id" in fdf.columns:
        mask |= fdf["student_id"].astype(str).str.contains(search, case=False, na=False)
    fdf = fdf[mask]
if class_filter and "class" in fdf.columns:
    fdf = fdf[fdf["class"].isin(class_filter)]
if risk_filter and "risk_level" in fdf.columns:
    fdf = fdf[fdf["risk_level"].isin(risk_filter)]
if "attendance_percent" in fdf.columns:
    fdf = fdf[fdf["attendance_percent"].between(min_att, max_att)]

# ---------------- KPIs ----------------
k1, k2, k3, k4 = st.columns(4)
metric_card("Matching Students", f"{len(fdf):,}", k1)
if "risk_score" in fdf.columns and len(fdf):
    metric_card("Avg Risk Score", f"{fdf['risk_score'].mean():.1f}", k2)
else:
    metric_card("Avg Risk Score", "—", k2)
if "risk_level" in fdf.columns and len(fdf):
    metric_card("High Risk Count", f"{(fdf['risk_level']=='High').sum():,}", k3)
else:
    metric_card("High Risk Count", "—", k3)
metric_card("Columns", f"{fdf.shape[1]}", k4)

st.markdown("---")

# ---------------- Table ----------------
st.markdown('<div class="section-title">Student Records</div>', unsafe_allow_html=True)
st.dataframe(fdf, use_container_width=True, height=460)

st.download_button(
    "⬇️ Download filtered data as CSV",
    data=fdf.to_csv(index=False).encode("utf-8"),
    file_name="students_filtered.csv",
    mime="text/csv",
    use_container_width=True,
)

st.caption(
    "Uploading a new CSV replaces the working dataset used across the Dashboard and this page. "
    "Use *Reset to sample dataset* to go back to the built-in demo data."
)