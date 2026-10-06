import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# Page Layout Configuration
st.set_page_config(
    page_title="AuditFlow Enterprise | Public Accounting Suite",
    page_icon="💼",
    layout="wide"
)

# Custom Professional Styling with Larger Fonts and Clean Layout
st.markdown("""
    <style>
    /* Increase overall body text size */
    html, body, [class*="css"] {
        font-size: 18px;
    }

    /* Make main titles and headers much larger and bolder */
    h1 {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #1e3a8a !important;
    }
    h2 {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
    }
    h3 {
        font-size: 1.6rem !important;
        font-weight: 600 !important;
    }

    /* Enhance metric cards styling and text size */
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    .stMetric label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
    }
    .stMetric div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }

    /* Sidebar text scaling */
    .sidebar .sidebar-content {
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💼 AuditFlow Enterprise")
st.markdown("### **Public Accounting & Forensic Audit Suite**")
st.markdown("Advanced AI-powered financial auditing, data hygiene inspection, and fraud detection platform.")

# 1. Load Dataset
file_path = "public_accountant_data_500.csv"
if not os.path.exists(file_path):
    st.error(f"Critical Error: Dataset file '{file_path}' not found in the project directory.")
    st.stop()

df = pd.read_csv(file_path)

# Clean numeric amounts
if 'Amount' in df.columns:
    amount_col = 'Amount'
elif 'Total' in df.columns:
    amount_col = 'Total'
else:
    amount_col = df.columns[-1]

df['Clean_Amount'] = pd.to_numeric(
    df[amount_col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False),
    errors='coerce'
).fillna(0)

# --- PROFESSIONAL SIDEBAR CONTROLS ---
st.sidebar.header("Control Panel")
navigation = st.sidebar.radio("Navigation Menu:", [
    "Executive Dashboard",
    "Interactive Transaction Explorer",
    "Forensic Fraud Detection (Benford's Law)",
    "Data Quality & Risk Center",
    "Client Portfolio Analytics"
])

st.sidebar.markdown("---")
st.sidebar.info("System Status: **Secure & Live**\nActive Dataset: `public_accountant_data_500.csv`")

# --- VIEW 1: EXECUTIVE DASHBOARD ---
if navigation == "Executive Dashboard":
    st.subheader("Executive Financial Summary")

    total_rev = df[df['Document_Type'] == 'Invoice']['Clean_Amount'].sum() if 'Document_Type' in df.columns else df[
        'Clean_Amount'].sum()
    total_exp = df[df['Document_Type'] == 'Receipt']['Clean_Amount'].sum() if 'Document_Type' in df.columns else 0
    net_position = total_rev - total_exp

    pending_cash = df[df['Status'] == 'Pending']['Clean_Amount'].sum() if 'Status' in df.columns else 0
    pending_count = len(df[df['Status'] == 'Pending']) if 'Status' in df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Billed Revenue", f"${total_rev:,.2f}", delta="Verified")
    col2.metric("Total Expenses", f"${total_exp:,.2f}")
    col3.metric("Net Financial Position", f"${net_position:,.2f}")
    col4.metric("Pending Receivables", f"${pending_cash:,.2f}", delta=f"{pending_count} Unpaid", delta_color="inverse")

    st.markdown("### **Quick Financial Volume by Client**")
    client_col = 'Client' if 'Client' in df.columns else df.columns[1]
    client_summary = df.groupby(client_col)['Clean_Amount'].sum().reset_index()

    st.bar_chart(client_summary.set_index(client_col))

# --- VIEW 2: INTERACTIVE TRANSACTION EXPLORER ---
elif navigation == "Interactive Transaction Explorer":
    st.subheader("Global Transaction Ledger & Search")
    st.markdown("Filter, search, and inspect the entire 500-row invoice database in real-time.")

    search_query = st.text_input("🔍 Search by Client Name or Invoice ID:", "")

    filtered_df = df
    if search_query:
        filtered_df = df[df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)]

    st.dataframe(filtered_df, use_container_width=True, height=450)
    st.caption(f"Showing {len(filtered_df)} matching transactions.")

# --- VIEW 3: BENFORD'S LAW FRAUD DETECTION ---
elif navigation == "Forensic Fraud Detection (Benford's Law)":
    st.subheader("Forensic Accounting: Benford's Law Digit Analysis")
    st.markdown("Public accounting forensic test used to detect anomalies, artificial data entry patterns, or fraud.")

    valid_amounts = df[df['Clean_Amount'] > 0]['Clean_Amount']
    first_digits = valid_amounts.astype(str).str.lstrip('0.').str[0].astype(int)
    actual_counts = first_digits.value_counts(normalize=True).sort_index() * 100

    benford_expected = {d: np.log10(1 + 1 / d) * 100 for d in range(1, 10)}

    benford_df = pd.DataFrame({
        'Leading Digit': list(benford_expected.keys()),
        'Expected Frequency (%)': [round(v, 2) for v in benford_expected.values()],
        'Actual Frequency (%)': [round(actual_counts.get(d, 0), 2) for d in range(1, 10)]
    })

    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(benford_df, use_container_width=True)
    with col2:
        st.warning(
            "⚠️ **Audit Interpretation:**\n\nIf the Actual frequency deviates significantly from the Expected Benford curve, the ledger may have been manually fabricated or altered.")

# --- VIEW 4: DATA QUALITY & RISK CENTER ---
elif navigation == "Data Quality & Risk Center":
    st.subheader("Data Hygiene & Entry Error Center")
    st.markdown("Automated checks targeting common public accounting data entry mistakes.")

    tab1, tab2, tab3 = st.tabs(["Duplicates & Outliers", "Category 'Misc' Trap", "Date Compliance"])

    with tab1:
        id_col = 'Invoice_ID' if 'Invoice_ID' in df.columns else df.columns[0]
        duplicates = df[df.duplicated(subset=[id_col], keep=False)]
        st.write(f"**Duplicate Invoice Check:** Found `{len(duplicates)}` rows with matching identifier markers.")
        if not duplicates.empty:
            st.dataframe(duplicates)

        mean_val = df['Clean_Amount'].mean()
        outliers = df[df['Clean_Amount'] > (mean_val * 4)]
        st.write(
            f"**Transposition / High-Value Outliers:** `{len(outliers)}` transactions exceed 4x portfolio average.")

    with tab2:
        cat_col = 'Category' if 'Category' in df.columns else None
        if cat_col:
            misc_filter = df[cat_col].astype(str).str.lower().isin(
                ['misc', 'miscellaneous', 'other', 'unclassified', 'nan'])
            st.write(
                f"**The 'Misc' Trap Analysis:** `{misc_filter.sum()}` items logged under uninformative categories.")
            st.dataframe(df[misc_filter].head(10))

    with tab3:
        date_col = 'Invoice_Date' if 'Invoice_Date' in df.columns else None
        if date_col:
            invalid_dates = pd.to_datetime(df[date_col], errors='coerce').isna().sum()
            st.write(f"**Period-Matching Date Check:** `{invalid_dates}` unparseable formatting structures found.")

# --- VIEW 5: CLIENT PORTFOLIO ANALYTICS ---
elif navigation == "Client Portfolio Analytics":
    st.subheader("Client Ledger & Outstanding Balances")

    client_col = 'Client' if 'Client' in df.columns else df.columns[1]
    portfolio_summary = df.groupby(client_col).agg(
        Total_Transactions=('Clean_Amount', 'count'),
        Cumulative_Volume=('Clean_Amount', 'sum')
    ).reset_index()

    st.dataframe(portfolio_summary.sort_values(by="Cumulative_Volume", ascending=False), use_container_width=True,
                 height=450)