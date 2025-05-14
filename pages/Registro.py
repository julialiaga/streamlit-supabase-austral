import streamlit as st
from functions import execute_query

st.title("Registro")

tipo = st.selectbox("¿Te registrás como?", ["Usuario", "Empresa"])

nombre = st.text_input("Nombre")
mail = st.text_input("Correo electrónico")
contrasena = st.text_input("Contraseña", type="password")
direccion = st.text_input("Dirección")
telefono = st.text_input("Teléfono (solo números)")

if tipo == "Empresa":
    cuit = st.text_input("CUIT (solo números)")

if st.button("Registrarme"):
    if not nombre or not mail or not contrasena or not telefono:
        st.warning("Por favor completá los campos obligatorios.")
    elif not telefono.isdigit():
        st.warning("El teléfono debe contener solo números.")
    elif tipo == "Empresa" and (not cuit or not cuit.isdigit()):
        st.warning("El CUIT debe contener solo números.")
    else:
        tabla = "empresa" if tipo == "Empresa" else "usuario"

        # Verificamos si ya existe ese correo
        check_query = f"SELECT * FROM {tabla} WHERE mail = '{mail}'"
        check_result = execute_query(check_query)

        if not check_result.empty:
            st.error("Ya existe una cuenta registrada con ese correo.")
        else:
            if tipo == "Empresa":
                insert_query = f"""
                    INSERT INTO empresa (nombre, mail, contrasena, direccion, telefono, cuit)
                    VALUES ('{nombre}', '{mail}', '{contrasena}', '{direccion}', '{telefono}', {int(cuit)})
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
                st.error("Ocurrió un error al registrar. Intentá de nuevo.")
