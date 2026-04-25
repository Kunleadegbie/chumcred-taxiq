import os
import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
from ai.assistant import analyze
from billing.subscription import has_active_subscription
from modules.reports import generate_firs_excel
from modules.admin import admin_panel
from modules.client_report import generate_client_report


# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
st.set_page_config(layout="wide")

# ✅ UI UPGRADE (SAFE)
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 1rem;}
</style>
""", unsafe_allow_html=True)

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
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if res.user:
            user_id = res.user.id

            supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "role": "client"
            }).execute()

            supabase.table("clients").insert({
                "user_id": user_id,
                "client_name": email.split("@")[0],
                "status": "active"
            }).execute()

            st.success("Account created successfully. Please login.")
        else:
            st.error("Signup failed")

# ------------------------------------------------------------
# LANDING PAGE (CONVERSION-FOCUSED 🔥 UPDATED)
# ------------------------------------------------------------
if not st.session_state.user:

    st.image("assets/chumcred_logo.png", width=180)  # ✅ LOGO

    st.markdown("""
    <h1 style='text-align: center;'>📊 Chumcred VAT & Business Intelligence Platform</h1>
    <h2 style='text-align: center;'>🚀 Stop VAT Stress. Track Profit. Grow Smarter.</h2>
    <p style='text-align: center; font-size:20px;'>
    Manage your VAT, generate FIRS-ready reports, and track your business profit — all in one place.
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
        st.write("Download compliant VAT reports in seconds.")

    with col3:
        st.success("💰 Track your profit automatically")
        st.write("Know your revenue, cost, and profit without separate accounting tools.")

    st.markdown("---")

    # PROBLEM / SOLUTION
    st.markdown("""
    ### ❗ Why This Matters

    Many businesses struggle with:
    - Manual VAT calculations  
    - Errors in tax reporting  
    - No visibility into profit and cost  
    - Time wasted preparing reports  

    ### ✅ Our Solution

    This platform helps you:
    - Track VAT effortlessly  
    - Generate accurate FIRS-ready reports instantly  
    - Monitor your cost, revenue, and profit in real time  
    - Use one system instead of multiple tools  
    """)

    st.markdown("---")

    # TRUST SIGNAL
    st.info(" Built for Nigerian businesses • FIRS-aligned format • Secure & private • Designed for simplicity")

    st.markdown("---")

    # STRONG CTA
    st.markdown("## 🚀 Get Started Now")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Create Account"])

    with tab1:
        st.subheader("Login to continue")
        login()

    with tab2:
        st.subheader("Start managing your VAT and profit in minutes")
        signup()

    st.stop()


# ------------------------------------------------------------
# USER SESSION
# ------------------------------------------------------------
user = st.session_state.user
user_id = user.id

res = supabase.table("users").select("id, role").execute()
user_row = next((r for r in res.data if r["id"] == user_id), None)

if user_row:
    role = user_row["role"]
elif user.email == "chumcred@gmail.com":
    role = "admin"
else:
    role = "client"

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
st.sidebar.markdown(f"👤 {user.email}")

menu = ["Dashboard", "Subscription"]

if role == "admin":
    menu.append("Admin Panel")

choice = st.sidebar.radio("Menu", menu)

# ------------------------------------------------------------
# CLIENT MANAGEMENT
# ------------------------------------------------------------
clients = supabase.table("clients").select("*").eq("user_id", user_id).execute()

if role == "admin":

    st.sidebar.header("Clients")

    new_client = st.sidebar.text_input("Add Client")

    if st.sidebar.button("Add Client"):
        supabase.table("clients").insert({
            "user_id": user_id,
            "client_name": new_client,
            "status": "active"
        }).execute()
        st.rerun()

    client_names = [c["client_name"] for c in clients.data]
    selected_client = st.sidebar.selectbox("Select Client", client_names)
    selected_client_data = next(c for c in clients.data if c["client_name"] == selected_client)
    client_id = selected_client_data["id"]

    # ✅ LOGOUT MOVED HERE
    if st.sidebar.button("🚪 Logout", key="logout_admin"):
        st.session_state.user = None
        st.rerun()

else:
    if clients.data:
        selected_client_data = clients.data[0]
        selected_client = selected_client_data["client_name"]
        client_id = selected_client_data["id"]

        # ✅ LOGOUT MOVED HERE
        if st.sidebar.button("🚪 Logout", key="logout_client"):
            st.session_state.user = None
            st.rerun()

    else:
        st.warning("Setting up your workspace...")
        supabase.table("clients").insert({
            "user_id": user_id,
            "client_name": user.email.split("@")[0],
            "status": "active"
        }).execute()
        st.rerun()

# ------------------------------------------------------------
# ADMIN PANEL
# ------------------------------------------------------------
if choice == "Admin Panel" and role == "admin":
    admin_panel(user)
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
    - Profit Tracking  
    """)

    receipt = st.file_uploader("Upload Payment Receipt")

    if st.button("Submit Payment"):
        supabase.table("subscriptions").insert({
            "user_id": user_id,
            "email": user.email,
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
    df["cost_price"] = df.get("cost_price", 0)
    df["profit"] = df["item_cost"] - df["cost_price"]

    revenue = df["item_cost"].sum()
    cost_total = df["cost_price"].sum()
    profit_total = df["profit"].sum()
    vat = revenue * 0.075

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Transactions", len(df))
    c2.metric("Revenue (₦)", f"{revenue:,.2f}")
    c3.metric("Cost (₦)", f"{cost_total:,.2f}")
    c4.metric("Profit (₦)", f"{profit_total:,.2f}")
    c5.metric("VAT Payable (₦)", f"{vat:,.2f}")

    # ✅ CHARTS
    st.markdown("---")
    st.subheader("📈 Business Insights")

    monthly = df.groupby("month")[["item_cost","cost_price","profit"]].sum()
    st.line_chart(monthly)

    st.subheader("🏆 Top Items")
    st.bar_chart(df.groupby("item")["profit"].sum().sort_values(ascending=False).head(5))

# ------------------------------------------------------------
# ADD RECORD
# ------------------------------------------------------------
st.subheader("➕ Add VAT Record")

month = st.selectbox("Month", [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
])

year = st.selectbox("Year", ["2024","2025","2026"])

name = st.text_input("Beneficiary Name")
tin = st.text_input("TIN")
item = st.text_input("Item")
cost = st.number_input("Item Cost", min_value=0.0)
cost_price = st.number_input("Cost Price", min_value=0.0)
desc = st.text_input("Description")

if st.button("Add Record"):
    supabase.table("vat_records").insert({
        "user_id": user_id,
        "client_id": client_id,
        "month": month,
        "year": year,
        "beneficiary_name": name,
        "beneficiary_tin": tin,
        "item": item,
        "item_cost": cost,
        "cost_price": cost_price,
        "item_description": desc,
        "vat_status": 0
    }).execute()
    st.success("Record added")
    st.rerun()

# ------------------------------------------------------------
# EXPORT
# ------------------------------------------------------------
st.subheader("📥 Export")

if has_active_subscription(user_id):

    if st.button("Download VAT Excel"):
        file = generate_firs_excel(df.to_dict("records"))
        st.download_button("Download VAT", file)

    if st.button("Download Client Report"):
        file = generate_client_report(df.to_dict("records"))
        st.download_button("Download Client Report", file)

else:
    st.warning("Upgrade to export")






