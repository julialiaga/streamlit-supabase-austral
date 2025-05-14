import streamlit as st

st.set_page_config(page_title="Login Empresa")

st.title("Inicio de Sesión - Empresa")
st.text_input("Correo electrónico")
st.text_input("Contraseña", type="password")
st.button("Iniciar sesión")
