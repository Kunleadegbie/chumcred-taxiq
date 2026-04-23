import streamlit as st
from core.database import get_supabase

supabase = get_supabase()

def client_sidebar(user_id):
    st.sidebar.header("Clients")

    res = supabase.table("clients").select("*").eq("user_id", user_id).execute()
    clients = res.data

    new_client = st.sidebar.text_input("Add Client")

    if st.sidebar.button("Add Client"):
        if new_client:
            supabase.table("clients").insert({
                "user_id": user_id,
                "client_name": new_client
            }).execute()
            st.rerun()

    if clients:
        names = [c["client_name"] for c in clients]
        selected = st.sidebar.selectbox("Select Client", names)
        client_id = next(c["id"] for c in clients if c["client_name"] == selected)
        return selected, client_id

    st.warning("Add a client to continue")
    st.stop()