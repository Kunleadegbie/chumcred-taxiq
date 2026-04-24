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
# LANDING PAGE
# ------------------------------------------------------------
if not st.session_state.user:
    st.markdown("<h1 style='text-align:center;'>🚀 VAT Intelligence Platform</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        login()
    with tab2:
        signup()

    st.stop()

# ------------------------------------------------------------
# USER SESSION
# ------------------------------------------------------------
user = st.session_state.user
user_id = user.id
role = user.user_metadata.get("role", "client")

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
st.sidebar.markdown(f"👤 {user.email}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

menu = ["Dashboard", "Subscription"]

if role == "admin":
    menu.append("Admin Panel")

choice = st.sidebar.radio("Menu", menu)

# ------------------------------------------------------------
# CLIENT MANAGEMENT (ROLE BASED)
# ------------------------------------------------------------
clients = supabase.table("clients").select("*").eq("user_id", user_id).execute()

# -------- ADMIN --------
if role == "admin":

    st.sidebar.header("Clients")

    new_client = st.sidebar.text_input("Add Client")

    if st.sidebar.button("Add Client"):
        if new_client:
            supabase.table("clients").insert({
                "user_id": user_id,
                "client_name": new_client,
                "status": "active"
            }).execute()
            st.rerun()

    if clients.data:
        names = [c["client_name"] for c in clients.data]
        selected_client = st.sidebar.selectbox("Select Client", names)
        selected_client_data = next(c for c in clients.data if c["client_name"] == selected_client)
        client_id = selected_client_data["id"]
    else:
        st.warning("Add a client")
        st.stop()

# -------- CLIENT --------
else:

    if clients.data:
        selected_client_data = clients.data[0]
        selected_client = selected_client_data["client_name"]
        client_id = selected_client_data["id"]
    else:
        st.error("No client assigned. Contact admin.")
        st.stop()

# Block check
if selected_client_data.get("status") == "blocked":
    st.error("🚫 Access blocked. Subscription required.")
    st.stop()

# ------------------------------------------------------------
# ADMIN PANEL
# ------------------------------------------------------------
if choice == "Admin Panel" and role == "admin":
    admin_panel(user)
    st.stop()

# ------------------------------------------------------------
# SUBSCRIPTION
# ------------------------------------------------------------
if choice == "Subscription":

    st.title("💳 Subscription")

    receipt = st.file_uploader("Upload Payment Receipt")

    if st.button("Submit Payment"):
        supabase.table("subscriptions").insert({
            "user_id": user_id,
            "email": user.email,
            "plan": "basic",
            "status": "pending"
        }).execute()

        st.success("Payment submitted")
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
st.title(f"📊 {selected_client}")

if not df.empty:
    revenue = df["item_cost"].sum()
    vat = revenue * 0.075

    c1, c2, c3 = st.columns(3)
    c1.metric("Transactions", len(df))
    c2.metric("Revenue", f"₦{revenue:,.2f}")
    c3.metric("VAT", f"₦{vat:,.2f}")
else:
    st.info("No data")

# ------------------------------------------------------------
# AI
# ------------------------------------------------------------
if has_active_subscription(user_id):
    if st.button("Analyze VAT"):
        st.write(analyze(df))
else:
    st.warning("Upgrade to use AI")

# ------------------------------------------------------------
# ADD RECORD
# ------------------------------------------------------------
st.subheader("Add VAT Record")

month = st.selectbox("Month", ["January","February","March"])
year = st.selectbox("Year", ["2025","2026"])

name = st.text_input("Name")
tin = st.text_input("TIN")
item = st.text_input("Item")
cost = st.number_input("Cost", min_value=0.0)
desc = st.text_input("Description")

if st.button("Add Record"):
    if cost <= 0:
        st.error("Cost required")
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
        st.success("Added")
        st.rerun()

# ------------------------------------------------------------
# TABLE
# ------------------------------------------------------------
st.subheader("Records")

if not df.empty:
    st.dataframe(df)