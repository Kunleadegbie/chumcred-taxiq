import streamlit as st
from core.constants import VAT_RATE

def show_dashboard(df, client_name):
    st.subheader(f"Dashboard — {client_name}")

    if df.empty:
        st.info("No data")
        return

    total_revenue = df["item_cost"].sum()
    vat = total_revenue * VAT_RATE

    c1, c2, c3 = st.columns(3)
    c1.metric("Transactions", len(df))
    c2.metric("Revenue (₦)", f"{total_revenue:,.2f}")
    c3.metric("VAT Payable (₦)", f"{vat:,.2f}")