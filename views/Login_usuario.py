import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.layout import set_background_color, add_logo_and_header, add_footer
from utils.db import execute_query

set_background_color()
add_logo_and_header()

st.title("Inicio de Sesión - Usuario")

correo = st.text_input("Correo electrónico")
contrasena = st.text_input("Contraseña", type="password")

if st.button("Iniciar sesión"):
    if not correo or not contrasena:
        st.warning("Por favor completá todos los campos.")
    else:
        query = f"SELECT * FROM usuario WHERE mail = '{correo}' AND contrasena = '{contrasena}'"
        resultado = execute_query(query)
        if not resultado.empty:
            st.success("Inicio de sesión exitoso.")
            st.session_state["vista"] = "vista_usuario"
            st.rerun()
        else:
            st.error("Correo o contraseña incorrectos.")


