import pandas as pd

df = pd.read_csv('Cleaned Copy of dataset.csv')
df = df.rename(columns={'name_customer': 'Client_Name'})

print(df.head())

import matplotlib.pyplot as plt
import os
import shutil
from datetime import datetime
import numpy as np

# 1. Dataset Configuration & Fail-Safe Backup Handler
file_path = r"C:\Users\vship\PublicAccountantCapstone\Cleaned Copy of dataset.csv"


# --- AUTOMATED BACKUP PROTOCOL ---
def create_dataset_backup():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_public_accountant_data_{timestamp}.csv"
        shutil.copy(file_path, backup_filename)
        print(f"[Backup System] Success: Secure backup created -> '{backup_filename}'")
    except Exception as e:
        print(f"[Backup System] Warning: Could not create backup file. Error: {e}")


create_dataset_backup()

file_path = r"Cleaned Copy of dataset.csv"

# Ensure Amount/Total is clean numeric
if 'Amount' in df.columns:
    amount_col = 'Amount'
elif 'Total' in df.columns:
    amount_col = 'Total'
else:
    amount_col = df.columns[-1]

df['Clean_Amount'] = pd.to_numeric(
    df[amount_col].astype(str).str.replace('£', '', regex=False).str.replace(',', '', regex=False),
    errors='coerce'
).fillna(0)


def show_dashboard():
    print("=" * 65)
    print("       AUDITFLOW: PUBLIC ACCOUNTING & FORENSIC AUDIT SUITE       ")
    print("=" * 65 + "\n")

    if 'Document_Type' in df.columns:
        total_rev = df[df['Document_Type'] == 'Invoice']['Clean_Amount'].sum()
        total_exp = df[df['Document_Type'] == 'Receipt']['Clean_Amount'].sum()
        print(f"Total Revenue (Invoices): £{total_rev:,.2f}")
        print(f"Total Expenses (Receipts): £{total_exp:,.2f}")

    if 'Status' in df.columns:
        pending = df[df['Status'] == 'Pending']
        print(f"[CASH FLOW ALERT] Pending Cash: £{pending['Clean_Amount'].sum():,.2f} ({len(pending)} unpaid invoices)")

    print("-" * 65)


def view_raw_invoices():
    print("\n--- RAW INVOICE DATABASE PREVIEW (First 10 Rows) ---")
    # Display a clean text table of the first 10 rows of your dataset
    print(df.head(10).to_string())
    print("-" * 65)


def run_benfords_law_audit():
    print("\n--- FORENSIC AUDIT: BENFORD'S LAW FRAUD DETECTION ---")
    print("Analyzing first-digit distribution of financial transactions...")

    valid_amounts = df[df['Clean_Amount'] > 0]['Clean_Amount']
    first_digits = valid_amounts.astype(str).str.lstrip('0.').str[0].astype(int)
    actual_counts = first_digits.value_counts(normalize=True).sort_index() * 100

    benford_expected = {d: np.log10(1 + 1 / d) * 100 for d in range(1, 10)}

    benford_df = pd.DataFrame({
        'Digit': list(benford_expected.keys()),
        'Expected_%': [round(v, 2) for v in benford_expected.values()],
        'Actual_%': [round(actual_counts.get(d, 0), 2) for d in range(1, 10)]
    })

    print(benford_df.to_string(index=False))
    print("\n[Audit Note] Significant deviation from Benford's Law indicates potential data tampering.\n")


def run_comprehensive_data_quality_audit():
    print("\n=================================================================")
    print("         COMPREHENSIVE DATA ENTRY & ERROR AUDIT SUITE            ")
    print("=================================================================\n")

    id_col = 'Invoice_ID' if 'Invoice_ID' in df.columns else df.columns[0]
    duplicates = df[df.duplicated(subset=[id_col], keep=False)]
    print(f"1. [Duplicate Check] Found {len(duplicates)} potential double-billed transaction rows matching ID fields.")

    if 'Client' in df.columns:
        raw_clients = df['Client'].dropna()
        print(f"2. [Naming Consistency] Total unique client spelling variations: {len(raw_clients.unique())}.")

    mean_val = df['Clean_Amount'].mean()
    outliers = df[df['Clean_Amount'] > (mean_val * 4)]
    print(
        f"3. [Transposition/Outliers] Flagged {len(outliers)} unusually extreme amount entries exceeding 4x portfolio average.")

    cat_col = 'Category' if 'Category' in df.columns else None
    if cat_col:
        misc_filter = df[cat_col].astype(str).str.lower().isin(
            ['misc', 'miscellaneous', 'other', 'unclassified', 'nan'])
        print(
            f"4. [Category Audit] Found {misc_filter.sum()} transactions lumped into vague categories ('Misc' / 'Other' / Blank).")

    date_col = 'Invoice_Date' if 'Invoice_Date' in df.columns else None
    if date_col:
        invalid_dates = pd.to_datetime(df[date_col], errors='coerce').isna().sum()
        print(
            f"5. [Date Compliance] Found {invalid_dates} unparseable or malformed date entries causing period-matching risks.")

    print("\n-----------------------------------------------------------------\n")


def view_client_breakdown():
    print(summary.to_string())
    print("-" * 65)


def export_client_reports():
    print("\n--- EXPORTING ALL CLIENT REPORTS ---")
    possible_names = ['name_customer', 'Client', 'Client_Name', 'Client Name', 'Name']
    client_col = next((col for col in possible_names if col in df.columns), None)

    if client_col is None:
        print(f"Error: None of {possible_names} found. Available columns: {list(df.columns)}")
        return

    unique_clients = df[client_col].dropna().unique()

    for client in unique_clients:
        client_data = df[df[client_col] == client]
        filename = f"{str(client).replace(' ', '_')}_audit_report.csv"
        client_data.to_csv(filename, index=False)
        print(f"[Saved] {filename} ({len(client_data)} records)")

    print("\nAll client audit reports exported successfully!\n")

def show_visual_chart():
    print("\nGenerating visual chart...")
    client_col = 'Client' if 'Client' in df.columns else df.columns[1]
    client_totals = df.groupby(client_col)['Clean_Amount'].sum()

    plt.figure(figsize=(10, 5))
    client_totals.plot(kind='bar', color='#2b6cb0', edgecolor='black')
    plt.title('AuditFlow: Financial Volume by Client')
    plt.xlabel('Client Name')
    plt.ylabel('Total Amount (£)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# --- INTERACTIVE APP LOOP ---
while True:
    show_dashboard()
    print("CHOOSE AN OPTION:")
    print("1. View General Financial Summary")
    print("2. Inspect Raw Invoices (Preview Database)")
    print("3. Run Benford's Law Fraud Detection Audit")
    print("4. Run Comprehensive Data Quality & Error Audit")
    print("5. View Client Portfolio Breakdown")
    print("6. Export Client Audit Reports (.csv)")
    print("7. Create Manual Data Backup File")
    print("8. Generate Visual Chart")
    print("9. Exit Application")

    choice = input("\nEnter your choice (1-9): ")

    if choice == '1':
        print("\n[Info] Dashboard summary displayed above.\n")
    elif choice == '2':
        view_raw_invoices()
    elif choice == '3':
        run_benfords_law_audit()
    elif choice == '4':
        run_comprehensive_data_quality_audit()
    elif choice == '5':
        view_client_breakdown()
    elif choice == '6':
        export_client_reports()
    elif choice == '7':
        create_dataset_backup()
    elif choice == '8':
        show_visual_chart()
    elif choice == '9':
        print("\nExiting AuditFlow. Professional session closed.")
        break
    else:
        print("\nInvalid choice. Please select an option between 1 and 9.\n")



# Find the correct column name dynamically
possible_names = ['Client_Name', 'Client Name', 'Client', 'Name']
client_col = next((col for col in possible_names if col in df.columns), None)

if client_col is None:
    raise KeyError(f"None of the expected client columns {possible_names} were found. Available columns are: {list(df.columns)}")

# Use the dynamically found column safely
unique_clients = df[client_col].dropna().unique()