import streamlit as st

st.title("My First Real App 🚀")

name = st.text_input("Enter your name")

if name:
    st.success(f"Hello {name} 👋")
