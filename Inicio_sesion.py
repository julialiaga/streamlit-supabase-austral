import streamlit as st
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from utils.layout import set_global_styles, add_logo_and_header, add_footer, load_css
from utils.db import execute_query



st.set_page_config(page_title="Ingreso", page_icon="🦾", layout="centered")

load_css("assets/style.css")

# Inicializar estados
if "tipo_login" not in st.session_state:
    st.session_state.tipo_login = None

if "vista" not in st.session_state:
    st.session_state["vista"] = "inicio"

# Estética general
set_global_styles()
add_logo_and_header()

# VISTA INICIO
if st.session_state["vista"] == "inicio":
    st.markdown("## ¿Cómo quieres ingresar?", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        if st.button("👤 Ingresar como Usuario"):
            st.session_state.tipo_login = "usuario"
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='width: 30px;'></div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
        if st.button("🏢 Ingresar como Empresa"):
            st.session_state.tipo_login = "empresa"
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.tipo_login:
        tipo = st.session_state.tipo_login
        st.markdown(f"### Inicio de sesión - {tipo.capitalize()}", unsafe_allow_html=True)

        correo = st.text_input("Correo electrónico", key="mail_" + tipo)
        contrasena = st.text_input("Contraseña", type="password", key="pass_" + tipo)

        if st.button("Iniciar sesión"):
            if not correo or not contrasena:
                st.warning("Por favor completá todos los campos.")
            else:
                tabla = "usuario" if tipo == "usuario" else "empresa"
                query = f"SELECT * FROM {tabla} WHERE mail = '{correo}' AND contrasena = '{contrasena}'"
                resultado = execute_query(query)

                if not resultado.empty:
                    st.success("Inicio de sesión exitoso.")
                    st.session_state[tipo] = resultado.iloc[0].to_dict()
                else:
                    st.error("Correo o contraseña incorrectos.")

        if st.button("⬅️ Volver"):
            st.session_state.tipo_login = None

    # Enlace a registro
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>¿No estás registrado? Hace click en <strong>Ir a registro</strong></p>", unsafe_allow_html=True)

    col = st.columns(3)
    with col[1]:
        if st.button("Ir a registro"):
            st.session_state["vista"] = "registro"
            st.rerun()

# VISTA REGISTRO
elif st.session_state["vista"] == "registro":
    from views import Registro
    Registro.mostrar()  # si definiste una función mostrar() en ese archivo

add_footer()
