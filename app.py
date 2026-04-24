import os
import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
from ai.assistant import analyze
from billing.subscription import has_active_subscription
from modules.reports import generate_firs_excel
from modules.admin import admin_panel


# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
st.set_page_config(layout="wide")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------------------------------------------------
# SESSION INIT
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# ------------------------------------------------------------
# AUTH FUNCTIONS
# ------------------------------------------------------------
def login():
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if res.user:
            st.session_state.user = res.user
            st.rerun()
        else:
            st.error("Invalid login details")


def signup():
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Create Account", key="signup_btn"):
        supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        st.success("Account created. You can now login.")

# ------------------------------------------------------------
# LANDING PAGE (CONVERSION-FOCUSED 🔥)
# ------------------------------------------------------------
if not st.session_state.user:

    st.markdown("""
    <h1 style='text-align: center;'>📊 Chumcred Limited VAT Intelligence Platform</h1>
    <h2 style='text-align: center;'>🚀 Stop VAT Stress. Stay Compliant. Save Time.</h2>
    <p style='text-align: center; font-size:20px;'>
    Track your VAT, generate FIRS-ready reports, and understand your numbers — all in one place.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # VALUE PROPOSITION
    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("💡 No more manual VAT tracking")
        st.write("Automate your VAT records and avoid costly errors.")

    with col2:
        st.success("📊 FIRS-ready reports instantly")
        st.write("Download compliant reports in seconds — no formatting stress.")

    with col3:
        st.success("🤖 Understand your VAT with AI")
        st.write("Get simple explanations and insights — no tax expertise needed.")

    st.markdown("---")

    # PROBLEM / SOLUTION
    st.markdown("""
    ### ❗ Why This Matters

    Many businesses struggle with:
    - Manual VAT calculations  
    - Errors in reporting  
    - Time wasted preparing returns  

    ### ✅ Our Solution

    This platform helps you:
    - Track VAT effortlessly  
    - Generate accurate reports instantly  
    - Understand your numbers clearly  
    """)

    st.markdown("---")

    # TRUST SIGNAL
    st.info(" This platform is designed for Nigerian businesses • FIRS-aligned format • Secure & private")

    st.markdown("---")

    # STRONG CTA
    st.markdown("## 🚀 Get Started Now")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Create Account"])

    with tab1:
        st.subheader("Login to continue")
        login()

    with tab2:
        st.subheader("Start managing your VAT in minutes")
        signup()

    st.stop()

# ------------------------------------------------------------
# USER SESSION
# ------------------------------------------------------------
user = st.session_state.user
user_id = user.id

# 🔥 FETCH ROLE FROM DATABASE (users table)
res = supabase.table("users").select("role").eq("id", user_id).execute()

if res.data:
    role = res.data[0]["role"]
else:
    role = "client"


# ------------------------------------------------------------
# SIDEBAR (WITH LOGOUT 🔥)
# ------------------------------------------------------------
st.sidebar.markdown(f"👤 {st.session_state.user.email}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.user = None
    st.rerun()

menu = ["Dashboard", "Subscription"]

if role == "admin":
    menu.append("Admin Panel")

choice = st.sidebar.radio("Menu", menu, key="menu_radio")

# ------------------------------------------------------------
# CLIENT MANAGEMENT (ROLE-BASED 🔥)
# ------------------------------------------------------------

clients = supabase.table("clients").select("*").eq("user_id", user_id).execute()

# ================= ADMIN VIEW =================
if role == "admin":

    st.sidebar.header("Clients")

    new_client = st.sidebar.text_input("Add Client", key="add_client_input")

    if st.sidebar.button("Add Client", key="add_client_btn"):
        if new_client:
            supabase.table("clients").insert({
                "user_id": user_id,
                "client_name": new_client,
                "status": "active"
            }).execute()
            st.rerun()

    if clients.data:
        client_names = [c["client_name"] for c in clients.data]
        selected_client = st.sidebar.selectbox("Select Client", client_names, key="client_select")
        selected_client_data = next(c for c in clients.data if c["client_name"] == selected_client)
        client_id = selected_client_data["id"]

    else:
        st.warning("Add a client")
        st.stop()

# ================= CLIENT VIEW =================
else:

    # Client sees ONLY their assigned client
    if clients.data:
        selected_client_data = clients.data[0]
        selected_client = selected_client_data["client_name"]
        client_id = selected_client_data["id"]

    else:
        st.error("No client assigned to your account. Contact admin.")
        st.stop()

# ------------------------------------------------------------
# ADMIN PANEL
# ------------------------------------------------------------
if choice == "Admin Panel" and role == "admin":
    admin_panel(st.session_state.user)
    st.stop()

# ------------------------------------------------------------
# SUBSCRIPTION PAGE
# ------------------------------------------------------------
if choice == "Subscription":

    st.title("💳 Subscription Plans")

    st.markdown("""
    ### Basic Plan — ₦10,000/month
    - VAT Management
    - AI Assistant
    - Excel Export
    """)

    receipt = st.file_uploader("Upload Payment Receipt", key="receipt_upload")

    if st.button("Submit Payment", key="submit_payment_btn"):
        supabase.table("subscriptions").insert({
            "user_id": user_id,
            "email": st.session_state.user.email,
            "plan": "basic",
            "status": "pending"
        }).execute()

        st.success("Payment submitted. Await approval.")

    st.stop()

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
records = supabase.table("vat_records")\
    .select("*")\
    .eq("user_id", user_id)\
    .eq("client_id", client_id)\
    .execute()

df = pd.DataFrame(records.data)

# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------
st.title(f"📊 Dashboard — {selected_client}")

if not df.empty:
    total_revenue = df["item_cost"].sum()
    vat = total_revenue * 0.075

    c1, c2, c3 = st.columns(3)
    c1.metric("Transactions", len(df))
    c2.metric("Revenue (₦)", f"{total_revenue:,.2f}")
    c3.metric("VAT Payable (₦)", f"{vat:,.2f}")
else:
    st.info("No data yet")

# ------------------------------------------------------------
# AI ASSISTANT
# ------------------------------------------------------------
st.subheader("🤖 AI Tax Assistant")

if not has_active_subscription(user_id):
    st.warning("🔒 AI Assistant is available on paid plans only")
else:
    if st.button("Analyze VAT Data", key="analyze_btn"):
        if df.empty:
            st.warning("No data available")
        else:
            result = analyze(df)
            st.success("Analysis Complete")
            st.write(result)

    user_question = st.text_input("Ask AI about tax", key="ai_question")

    if st.button("Ask AI", key="ask_ai_btn"):
        if user_question:
            response = analyze(pd.DataFrame({"question": [user_question]}))
            st.write(response)

# ------------------------------------------------------------
# ADD RECORD
# ------------------------------------------------------------
st.subheader("➕ Add VAT Record")

month = st.selectbox("Month", [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
], key="month_select")

year = st.selectbox("Year", ["2024","2025","2026"], key="year_select")

name = st.text_input("Beneficiary Name", key="vat_name")
tin = st.text_input("TIN", key="vat_tin")
item = st.text_input("Item", key="vat_item")
cost = st.number_input("Item Cost", min_value=0.0, key="vat_cost")
desc = st.text_input("Description", key="vat_desc")

if st.button("Add Record", key="add_record_btn"):
    if not all([name, tin, item, desc]) or cost <= 0:
        st.error("Fill all fields correctly")
    else:
        supabase.table("vat_records").insert({
            "user_id": user_id,
            "client_id": client_id,
            "month": month,
            "year": year,
            "beneficiary_name": name,
            "beneficiary_tin": tin,
            "item": item,
            "item_cost": cost,
            "item_description": desc,
            "vat_status": 0
        }).execute()
        st.success("Record added")
        st.rerun()

# ------------------------------------------------------------
# TABLE
# ------------------------------------------------------------
st.subheader("📋 VAT Records")

if df.empty:
    st.info("No VAT records available")
else:
    client_map = {c["id"]: c["client_name"] for c in clients.data}
    df["Client Name"] = df["client_id"].map(client_map)

    vat_map = {0: "VATABLE", 1: "ZERO RATED", 2: "EXEMPT"}
    df["VAT Status"] = df["vat_status"].map(vat_map)

    df_display = df.rename(columns={
        "month": "Month",
        "year": "Year",
        "beneficiary_name": "Beneficiary",
        "item": "Item",
        "item_cost": "Cost (₦)"
    })

    df_display = df_display[
        ["Client Name", "Month", "Year", "Beneficiary", "Item", "Cost (₦)", "VAT Status"]
    ]

    st.dataframe(df_display, use_container_width=True)

# ------------------------------------------------------------
# EXPORT
# ------------------------------------------------------------
st.subheader("📥 Export")

if not has_active_subscription(user_id):
    st.warning("🔒 Export is available on paid plans only")
else:
    if st.button("Download VAT Excel", key="download_btn"):
        excel_file = generate_firs_excel(df.to_dict("records"))

        st.download_button(
            "Download",
            excel_file,
            file_name=f"{selected_client}_VAT_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )