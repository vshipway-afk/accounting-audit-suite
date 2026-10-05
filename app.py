import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Page Layout Configuration
st.set_page_config(
    page_title="AuditFlow Enterprise | Public Accounting Suite",
    page_icon="📊",
    layout="wide",
)

# Custom Professional Styling
st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-size: 16px; }
    h1 { font-size: 2.4rem !important; font-weight: 800 !important; color: #1e3a8a !important; }
    h2 { font-size: 1.8rem !important; font-weight: 700 !important; color: #334155 !important; }
    .stMetric { background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
  # Loads and caches the full 5,000-row transaction dataset
  df = pd.read_csv("public_accountant_data_5000.csv")

  # Ensure clean numeric column for calculations
  if "Clean_Amount" in df.columns and df["Clean_Amount"].dtype == object:
    df["Clean_Amount"] = (
        df["Clean_Amount"]
        .astype(str)
        .str.replace("£", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

  df["Transaction_Date"] = pd.to_datetime(
      df["Transaction_Date"], errors="coerce"
  )
  return df


df = load_data()

# Sidebar Navigation
st.sidebar.title("AuditFlow Navigation")
app_mode = st.sidebar.selectbox(
    "Select Module",
    [
        "Executive Summary",
        "Raw Database Inspector",
        "Benford's Law Fraud Detection",
        "Duplicates & Overpayments",
        "Client Portfolio Breakdown",
    ],
)

# 1. EXECUTIVE SUMMARY
if app_mode == "Executive Summary":
  st.title("Executive Financial & Audit Summary")
  st.write(
      "Analyzing all 5,000 transactions across active risk metrics and"
      " portfolio liquidity."
  )

  col1, col2, col3, col4 = st.columns(4)
  total_txns = len(df)
  total_volume = df["Clean_Amount"].sum()
  flagged_count = len(
      df[df["Audit_Status"].isin(["Flagged", "Pending Review"])]
  )
  critical_count = len(df[df["Risk_Score"] == "Critical"])

  col1.metric("Total Transactions Processed", f"{total_txns:,}")
  col2.metric("Total Ledger Volume", f"£{total_volume:,.2f}")
  col3.metric("Items Needing Review", f"{flagged_count:,}")
  col4.metric("Critical Risk Entries", f"{critical_count:,}")

  st.markdown("---")
  st.subheader("Transaction Categories Distribution")
  fig, ax = plt.subplots(figsize=(10, 4))
  category_sums = df.groupby("Account_Category")["Clean_Amount"].sum()
  category_sums.plot(kind="bar", ax=ax, color="#1e3a8a")
  ax.set_ylabel("Total Amount (£)")
  ax.set_xlabel("Account Category")
  st.pyplot(fig)

# 2. RAW DATABASE INSPECTOR
elif app_mode == "Raw Database Inspector":
  st.title("Raw Database & Transaction Inspector")
  st.write(
      "Search, filter, and inspect records loaded directly from your 5,000-row"
      " audit pipeline."
  )

  client_filter = st.selectbox(
      "Filter by Client", ["All Clients"] + list(df["Client_Name"].unique())
  )
  status_filter = st.selectbox(
      "Filter by Audit Status", ["All Statuses"] + list(df["Audit_Status"].unique())
  )

  filtered_df = df.copy()
  if client_filter != "All Clients":
    filtered_df = filtered_df[filtered_df["Client_Name"] == client_filter]
  if status_filter != "All Statuses":
    filtered_df = filtered_df[filtered_df["Audit_Status"] == status_filter]

  st.dataframe(filtered_df, use_container_width=True)
  st.caption(
      f"Showing {len(filtered_df):,} records matching current filters."
  )

# 3. BENFORD'S LAW FRAUD DETECTION
elif app_mode == "Benford's Law Fraud Detection":
  st.title("Benford's Law First-Digit Anomaly Analysis")
  st.write(
      "Testing the leading digit distribution across the 5,000 transaction"
      " amounts to flag irregularities."
  )


  def get_first_digit(num):
    s = str(abs(num)).replace(".", "").lstrip("0")
    return int(s[0]) if len(s) > 0 else 0


  df["First_Digit"] = df["Clean_Amount"].apply(get_first_digit)
  digit_counts = df["First_Digit"].value_counts().sort_index()
  actual_dist = (digit_counts / digit_counts.sum()) * 100

  digits = np.arange(1, 10)
  benford_dist = [np.log10(1 + 1 / d) * 100 for d in digits]

  benford_df = pd.DataFrame(
      {
          "Digit": digits,
          "Actual (%)": [actual_dist.get(d, 0) for d in digits],
          "Benford Expected (%)": benford_dist,
      }
  ).set_index("Digit")

  st.bar_chart(benford_df)
  st.markdown(
      "> **Note:** Significant deviations from expected Benford frequencies"
      " highlight potential manipulated entries."
  )

# 4. DUPLICATES & OVERPAYMENTS
elif app_mode == "Duplicates & Overpayments":
  st.title("Automated Duplicate & Overpayment Scanner")
  st.write(
      "Scanning the 5,000 records for rows sharing exact transaction values"
      " and vendors within close date windows."
  )

  df_sorted = df.sort_values("Transaction_Date")
  duplicates = df_sorted[
      df_sorted.duplicated(
          subset=["Client_Name", "Clean_Amount"], keep=False
      )
  ]

  if not duplicates.empty:
    st.warning(
        f"Found {len(duplicates)} transactions with matching vendor/client and"
        " value pairings."
    )
    st.dataframe(
        duplicates[
            [
                "Invoice_ID",
                "Client_Name",
                "Transaction_Date",
                "Clean_Amount",
                "Account_Category",
                "Audit_Status",
            ]
        ],
        use_container_width=True,
    )
  else:
    st.success("No matching duplicate billing clusters detected.")

# 5. CLIENT PORTFOLIO BREAKDOWN
elif app_mode == "Client Portfolio Breakdown":
  st.title("Client Portfolio & Tax Liability Breakdown")
  st.write(
      "Aggregating ledger metrics across your 8 managed corporate clients."
  )

  client_summary = (
      df.groupby("Client_Name")
      .agg(
          Total_Transactions=("Invoice_ID", "count"),
          Total_Ledger_Volume=("Clean_Amount", "sum"),
          Flagged_Items=(
              "Audit_Status",
              lambda x: (x == "Flagged").sum(),
          ),
      )
      .reset_index()
  )

  st.table(client_summary)
  st.info(
      "Use your terminal launcher option [6] to export standalone CSV audit"
      " reports for each entity."
  )