import streamlit as st
import pandas as pd
from core.database import get_supabase
from core.constants import VAT_RATE
from utils.emailer import send_email_to_user

supabase = get_supabase()

import os

def is_admin(user):
    admin_email = os.getenv("ADMIN_EMAIL")
    return user.email == admin_email

def admin_panel(user):

    st.title("🛠 Admin Panel")

    st.subheader("📊 User Overview")

    subs = supabase.table("subscriptions").select("*").execute()

    if not subs.data:
        st.info("No subscriptions yet")
        return

    users_df = pd.DataFrame(subs.data)

    for _, u in users_df.iterrows():

        user_id = u["user_id"]
        user_email = u.get("email", "No Email")

        # -------------------------------
        # CLIENTS
        # -------------------------------
        clients_res = supabase.table("clients").select("*").eq("user_id", user_id).execute()
        clients = clients_res.data

        num_clients = len(clients)

        # -------------------------------
        # VAT RECORDS
        # -------------------------------
        records = supabase.table("vat_records").select("*").eq("user_id", user_id).execute()
        df = pd.DataFrame(records.data)

        if not df.empty:
            revenue = df["item_cost"].sum()
            vat = revenue * VAT_RATE
            transactions = len(df)
        else:
            revenue = 0
            vat = 0
            transactions = 0

        st.markdown("---")

        # -------------------------------
        # USER DISPLAY (NO IDS)
        # -------------------------------
        st.markdown(f"### 👤 {user_email}")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Clients", num_clients)
        c2.metric("Transactions", transactions)
        c3.metric("Revenue", f"₦{revenue:,.2f}")
        c4.metric("VAT", f"₦{vat:,.2f}")

        st.write(f"**Subscription Status:** {u['status']}")

        # ------------------------------------------------------------
        # CLIENT CONTROL (BY NAME 🔥)
        # ------------------------------------------------------------
        st.subheader("🏢 Clients")

        if not clients:
            st.info("No clients for this user")
        else:
            for c in clients:

                col1, col2, col3 = st.columns([4,2,2])

                col1.write(f"**{c['client_name']}**")
                col2.write(f"Status: {c.get('status', 'active')}")

                if c.get("status", "active") == "active":
                    if col3.button(f"Block {c['client_name']}", key=f"block_{c['id']}"):
                        supabase.table("clients").update({
                            "status": "blocked"
                        }).eq("id", c["id"]).execute()

                        st.warning(f"{c['client_name']} blocked")
                        st.rerun()

                else:
                    if col3.button(f"Unblock {c['client_name']}", key=f"unblock_{c['id']}"):
                        supabase.table("clients").update({
                            "status": "active"
                        }).eq("id", c["id"]).execute()

                        st.success(f"{c['client_name']} unblocked")
                        st.rerun()

        # ------------------------------------------------------------
        # SUBSCRIPTION ACTIONS
        # ------------------------------------------------------------
        st.subheader("💳 Subscription Control")

        colA, colB = st.columns(2)

        if u["status"] == "pending":
            if colA.button(f"Approve {user_email}", key=f"approve_{u['id']}"):

                # Activate subscription
                supabase.table("subscriptions").update({
                    "status": "active"
                }).eq("id", u["id"]).execute()

                # 🔥 UNBLOCK ALL CLIENTS
                supabase.table("clients").update({
                    "status": "active"
                }).eq("user_id", user_id).execute()

                send_email(user_email, "approved")
                st.success("Subscription approved & clients unlocked")
                st.rerun()

        if u["status"] == "active":
            if colB.button(f"Deactivate {user_email}", key=f"deactivate_{u['id']}"):

                supabase.table("subscriptions").update({
                    "status": "inactive"
                }).eq("id", u["id"]).execute()

                # 🔥 BLOCK ALL CLIENTS
                supabase.table("clients").update({
                    "status": "blocked"
                }).eq("user_id", user_id).execute()

                send_email(user_email, "deactivated")
                st.warning("Subscription deactivated & clients blocked")
                st.rerun()


# ------------------------------------------------------------
# EMAIL FUNCTION (SAFE — NO ADMIN API)
# ------------------------------------------------------------
def send_email(email, action):

    if action == "approved":
        subject = "Subscription Approved"
        body = "Your subscription is now active. All your clients have been unlocked."

    elif action == "deactivated":
        subject = "Subscription Deactivated"
        body = "Your subscription is inactive. All your clients are currently blocked."

    send_email_to_user(email, subject, body)