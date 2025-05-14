import streamlit as st

st.set_page_config(page_title="Ingreso", page_icon="🦾", layout="centered")

st.markdown("<h1 style='text-align: center;'>¿Cómo quieres ingresar?</h1>", unsafe_allow_html=True)
st.markdown("###")

col1, col2 = st.columns(2)

with col1:
    if st.button("👤 Usuario"):
        st.switch_page("pages/Login_usuario.py")

with col2:
    if st.button("🏢 Empresa"):
        st.switch_page("pages/Login_empresa.py")

st.markdown("---")

st.markdown("<p style='text-align: center;'>¿No estás registrado?</p>", unsafe_allow_html=True)

if st.button("📋 Hace click aquí para registrarte"):
    st.switch_page("pages/Registro.py")
