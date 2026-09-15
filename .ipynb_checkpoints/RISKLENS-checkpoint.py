import streamlit as st
import pandas as pd
import numpy as np

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="RISK LENS | STUDENT RISK ANALYTICS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)
def add_risk_columns(df):
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

    df["risk_level"] = np.where(
        df["RiskScore"] > 60, "High Risk",
        np.where(df["RiskScore"] > 35, "Medium Risk", "Low Risk")
    )
    return df

# ----------------------------------------------------------------------
# CUSTOM CSS — LOGO, TYPOGRAPHY, CARDS
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #0E1117;
    }

    /* ---------- LOGO ---------- */
    .logo-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        margin-top: 10px;
        margin-bottom: 6px;
    }
    .logo-icon {
        width: 70px;
        height: 70px;
        border-radius: 18px;
        background: linear-gradient(135deg, #FF4B4B 0%, #FFA53D 50%, #FFD23D 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        box-shadow: 0 0 25px rgba(255, 75, 75, 0.45);
    }
    .logo-text {
        font-size: 46px;
        font-weight: 900;
        letter-spacing: 4px;
        background: linear-gradient(90deg, #FF4B4B, #FFA53D, #FFD23D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .logo-sub {
        text-align: center;
        letter-spacing: 6px;
        font-size: 14px;
        font-weight: 600;
        color: #9AA0A6;
        margin-top: -6px;
        margin-bottom: 30px;
    }

    /* ---------- HERO ---------- */
    .hero-title {
        text-align: center;
        font-size: 30px;
        font-weight: 800;
        letter-spacing: 1.5px;
        color: #FAFAFA;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        text-align: center;
        font-size: 16px;
        font-weight: 500;
        letter-spacing: 1px;
        color: #B5B9C0;
        margin-bottom: 30px;
    }

    /* ---------- FEATURE CARDS ---------- */
    .card {
        background: #161A23;
        border: 1px solid #2A2F3A;
        border-radius: 14px;
        padding: 22px 18px;
        height: 100%;
        transition: 0.2s;
    }
    .card:hover {
        border-color: #FF4B4B;
        transform: translateY(-3px);
    }
    .card-title {
        font-size: 16px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #FAFAFA;
        margin-bottom: 8px;
    }
    .card-icon {
        font-size: 28px;
        margin-bottom: 10px;
    }
    .card-text {
        font-size: 13.5px;
        color: #9AA0A6;
        line-height: 1.5;
    }

    /* ---------- SECTION HEADERS ---------- */
    .section-header {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 2px;
        color: #FAFAFA;
        border-left: 5px solid #FF4B4B;
        padding-left: 12px;
        margin-top: 40px;
        margin-bottom: 18px;
    }

    /* ---------- UPLOAD GATE BOX ---------- */
    .upload-box {
        border: 2px dashed #FF4B4B;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 25px;
        background: #161A23;
    }

    /* ---------- FOOTER ---------- */
    .footer {
        text-align: center;
        color: #6C7078;
        font-size: 12px;
        letter-spacing: 1px;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #2A2F3A;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# LOGO / HEADER (always shown)
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class="logo-wrap">
        <div class="logo-icon">🎯</div>
        <div class="logo-text">RISK LENS</div>
    </div>
    <div class="logo-sub">S T U D E N T &nbsp; R I S K &nbsp; A N A L Y T I C S</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-title">EARLY WARNING SYSTEM FOR STUDENT SUCCESS</div>
    <div class="hero-subtitle">
        UPLOAD YOUR STUDENT DATA &nbsp;•&nbsp; DETECT AT-RISK STUDENTS &nbsp;•&nbsp; ACT BEFORE IT'S TOO LATE
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎯 RISK LENS")
    st.caption("STUDENT RISK ANALYTICS PLATFORM")
    st.divider()
    st.markdown("*DATASET STATUS*")
    if "student_df" in st.session_state:
        st.success(f"LOADED: {st.session_state['student_df'].shape[0]} STUDENTS")
        if st.button("REMOVE DATASET", use_container_width=True):
            del st.session_state["student_df"]
            st.rerun()
    else:
        st.warning("NO DATA UPLOADED YET")

# ----------------------------------------------------------------------
# MANDATORY UPLOAD GATE
# ----------------------------------------------------------------------
if "student_df" not in st.session_state:

    st.markdown('<div class="section-header">STEP 1 — UPLOAD YOUR STUDENT DATA</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="upload-box">
            <h4 style="color:#FAFAFA; letter-spacing:1px;">NO DATASET LOADED</h4>
            <p style="color:#9AA0A6;">
                UPLOAD A CSV OR EXCEL FILE CONTAINING YOUR STUDENT DATA TO UNLOCK
                THE DASHBOARD, RISK SCORES, AND REPORTS.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "CHOOSE A CSV OR EXCEL FILE",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=False,
    )
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            required_cols = ["AttendancePercent", "AssignmentSubmissionRate", "Test1_Score", "Test2_Score", "Test3_Score"]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                st.error(f"Uploaded file is missing required columns: {missing}")
                st.stop()

            df = add_risk_columns(df)

            if df.empty:
 
                st.error("THE UPLOADED FILE IS EMPTY. PLEASE CHECK THE FILE AND TRY AGAIN.")
            else:
                st.session_state["student_df"] = df
                st.success(f"✅ LOADED {df.shape[0]} ROWS AND {df.shape[1]} COLUMNS. RELOADING DASHBOARD...")
                st.rerun()

        except Exception as e:
            st.error(f"COULD NOT READ THE FILE. ERROR DETAILS: {e}")

    # Explain what the app does WHILE waiting for the upload, then stop.
    st.markdown('<div class="section-header">WHAT RISK LENS WILL DO ONCE DATA IS LOADED</div>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown(
            """
            <div class="card">
                <div class="card-icon">📊</div>
                <div class="card-title">DASHBOARD</div>
                <div class="card-text">VISUALIZE ATTENDANCE, GRADES, AND ENGAGEMENT TRENDS ACROSS YOUR STUDENTS.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            """
            <div class="card">
                <div class="card-icon">🧠</div>
                <div class="card-title">RISK SCORING</div>
                <div class="card-text">EACH STUDENT IS SCORED AS LOW, MEDIUM, OR HIGH RISK.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            """
            <div class="card">
                <div class="card-icon">🚩</div>
                <div class="card-title">EARLY FLAGS</div>
                <div class="card-text">STUDENTS LIKELY TO FALL BEHIND ARE SURFACED AUTOMATICALLY.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f4:
        st.markdown(
            """
            <div class="card">
                <div class="card-icon">📑</div>
                <div class="card-title">REPORTS</div>
                <div class="card-text">EXPORT SHAREABLE REPORTS FOR TEACHERS AND ADMINISTRATORS.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="footer">
            RISK LENS &nbsp;•&nbsp; STUDENT RISK ANALYTICS &nbsp;•&nbsp; BUILT WITH STREAMLIT
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Stop execution here — nothing below runs until data is uploaded.
    st.stop()

# ----------------------------------------------------------------------
# EVERYTHING BELOW ONLY RUNS AFTER DATA IS UPLOADED
# ----------------------------------------------------------------------
df = st.session_state["student_df"]

st.markdown('<div class="section-header">OVERVIEW</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

total = len(df)
if "risk_level" in df.columns:
    high_risk = int(df["risk_level"].astype(str).str.lower().str.contains("high").sum())
    med_risk = int(df["risk_level"].astype(str).str.lower().str.contains("medium").sum())
    low_risk = total - high_risk - med_risk
else:
    high_risk, med_risk, low_risk = 0, 0, 0

col1.metric("TOTAL STUDENTS", total)
col2.metric("HIGH RISK", high_risk)
col3.metric("MEDIUM RISK", med_risk)
col4.metric("LOW RISK", low_risk)

if "risk_level" not in df.columns:
    st.info(
        "NO 'risk_level' COLUMN FOUND IN YOUR DATA. "
        "RISK COUNTS WILL SHOW AS ZERO UNTIL RISK SCORING IS ADDED FOR YOUR SCHEMA."
    )

st.markdown('<div class="section-header">DATA PREVIEW</div>', unsafe_allow_html=True)
st.dataframe(df.head(20), use_container_width=True)

st.markdown('<div class="section-header">COLUMN SUMMARY</div>', unsafe_allow_html=True)
st.write(
    pd.DataFrame(
        {
            "COLUMN": df.columns,
            "DTYPE": df.dtypes.astype(str).values,
            "MISSING VALUES": df.isna().sum().values,
        }
    )
)

st.markdown(
    """
    <div class="footer">
        RISK LENS &nbsp;•&nbsp; STUDENT RISK ANALYTICS &nbsp;•&nbsp; BUILT WITH STREAMLIT
    </div>
    """,
    unsafe_allow_html=True,
)