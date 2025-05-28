import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.layout import set_background_color, add_logo_and_header, add_footer
from utils.db import execute_query

st.set_page_config(page_title="Registro")
set_background_color()
add_logo_and_header()

st.title("Registro de Cuenta")

tipo = st.selectbox("¿Te registrás como?", ["Usuario", "Empresa"])
nombre = st.text_input("Nombre")
mail = st.text_input("Correo electrónico")
contrasena = st.text_input("Contraseña", type="password")
direccion = st.text_input("Dirección")
telefono = st.text_input("Teléfono (solo números)")
cuit = st.text_input("CUIT (solo si sos empresa)") if tipo == "Empresa" else None

if st.button("Registrarme"):
    if not nombre or not mail or not contrasena or not direccion or not telefono:
        st.warning("Por favor completá todos los campos obligatorios.")
    elif tipo == "Empresa" and (not cuit or not cuit.isdigit()):
        st.warning("El CUIT debe contener solo números.")
    elif not telefono.isdigit():
        st.warning("El teléfono debe contener solo números.")
    else:
        tabla = "empresa" if tipo == "Empresa" else "usuario"
        check_query = f"SELECT * FROM {tabla} WHERE mail = '{mail}'"
        existe = execute_query(check_query)
        if not existe.empty:
            st.error("Ya existe una cuenta registrada con ese correo.")
        else:
            if tipo == "Empresa":
                insert_query = f"""
                    INSERT INTO empresa (nombre, mail, contrasena, direccion, telefono, cuit)
                    VALUES ('{nombre}', '{mail}', '{contrasena}', '{direccion}', '{telefono}', '{cuit}')
                """
            else:
                insert_query = f"""
                    INSERT INTO usuario (nombre, mail, contrasena, direccion, telefono)
                    VALUES ('{nombre}', '{mail}', '{contrasena}', '{direccion}', '{telefono}')
                """
            success = execute_query(insert_query, is_select=False)
            if success:
                st.success("Registro exitoso. Ya podés iniciar sesión.")
            else:
                st.error("Ocurrió un error durante el registro.")

add_footer()
