import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from utils.layout import set_background_color, add_logo_and_header, add_footer
from utils.db import execute_query

st.set_page_config(page_title="Ingreso", page_icon="🦾", layout="centered")
set_background_color()
add_logo_and_header()

# Estados para controlar qué formulario mostrar
if "tipo_login" not in st.session_state:
    st.session_state.tipo_login = None

st.markdown("<h3 style='text-align: center; color: #A5D8FF;'>¿Cómo quieres ingresar?</h3>", unsafe_allow_html=True)

# ---------- CSS para estilo tipo “card” + centrado ----------
st.markdown("""
    <style>
        .card-container {
            display: flex;
            justify-content: center;
            gap: 60px;
            margin-top: 30px;
        }
        .label {
            text-align: center;
            color: #A5D8FF;
            font-weight: 600;
            margin-top: 5px;
        }
        .centered-buttons {
            display: flex;
            justify-content: center;
            gap: 50px;
            margin-top: 30px;
        }
        .register-text {
            text-align: center;
            color: #CBD5E1;
            margin-top: 40px;
        }
        .register-text a {
            color: #A5D8FF;
            text-decoration: underline;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Botones centrados y alineados lado a lado ----------
col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
    if st.button("👤 Ingresar como Usuario"):
        st.session_state.tipo_login = "usuario"
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div style='width: 30px;'></div>", unsafe_allow_html=True)  # Espacio intermedio

with col3:
    st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
    if st.button("🏢 Ingresar como Empresa"):
        st.session_state.tipo_login = "empresa"
    st.markdown("</div>", unsafe_allow_html=True)


# ---------- Mostrar formulario según tipo ----------
if st.session_state.tipo_login:
    tipo = st.session_state.tipo_login
    st.markdown(f"<h4 style='color:#A5D8FF'>Inicio de sesión - {tipo.capitalize()}</h4>", unsafe_allow_html=True)

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

# ---------- Texto + botón clásico para registro ----------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #CBD5E1;'>¿No estás registrado? Hace click en <strong>Ir a registro</strong></p>", unsafe_allow_html=True)

# Botón centrado
col = st.columns(3)
with col[1]:  # botón en el medio
    if st.button("Ir a registro"):
        st.switch_page("pages/Registro.py")


add_footer()
