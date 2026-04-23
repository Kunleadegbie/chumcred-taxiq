import streamlit as st
from core.constants import MONTHS, YEARS
from core.database import get_supabase

supabase = get_supabase()

def vat_form(user_id, client_id):

    st.subheader("Add VAT Record")

    col1, col2, col3 = st.columns(3)

    with col1:
        month = st.selectbox("Month", MONTHS)

    with col2:
        year = st.selectbox("Year", YEARS)

    with col3:
        st.text_input("VAT Status", value="0", disabled=True)

    col4, col5 = st.columns(2)

    with col4:
        name = st.text_input("Beneficiary Name")
        tin = st.text_input("TIN")
        item = st.text_input("Item")

    with col5:
        cost = st.number_input("Item Cost", min_value=0.0)
        desc = st.text_input("Description")

    if st.button("Add Record"):
        if not all([name, tin, item, desc]) or cost <= 0:
            st.error("Complete all fields")
            return

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

        st.success("Saved")
        st.rerun()