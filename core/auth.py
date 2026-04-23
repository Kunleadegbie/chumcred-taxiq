import streamlit as st
from core.database import get_supabase

supabase = get_supabase()

def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None

def login_ui():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if res.user:
            st.session_state.user = res.user
            st.rerun()
        else:
            st.error("Invalid login")

def signup_ui():
    st.subheader("Signup")
    email = st.text_input("New Email")
    password = st.text_input("New Password", type="password")

    if st.button("Create Account"):
        supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        st.success("Account created")

def require_auth():
    if not st.session_state.user:
        tab1, tab2 = st.tabs(["Login", "Signup"])
        with tab1:
            login_ui()
        with tab2:
            signup_ui()
        st.stop()