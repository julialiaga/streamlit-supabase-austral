import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query

def mostrar():
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("registro")

    st.markdown('<h2 class="registro-title">Registro de Cuenta</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tipo = st.selectbox("¿Te registrás como?", ["Usuario", "Empresa"], help="Selecciona el tipo de cuenta que deseas crear")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre", placeholder="Ingresa tu nombre completo")
        mail = st.text_input("Correo electrónico", placeholder="ejemplo@correo.com")
        contrasena = st.text_input("Contraseña", type="password", placeholder="Crea una contraseña segura")

    with col2:
        direccion = st.text_input("Dirección", placeholder="Calle, número, ciudad")
        telefono = st.text_input("Teléfono", placeholder="Solo números (ej: 1123456789)")
        cuit = st.text_input("CUIT", placeholder="Solo números (ej: 20123456789)") if tipo == "Empresa" else None

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn1:
        if st.button("⬅ Volver", use_container_width=True):
            st.session_state["vista"] = "inicio"
            st.rerun()

    with col_btn3:
        if st.button("Registrarme", use_container_width=True, type="primary"):
            errores = []

            if not all([nombre, mail, contrasena, direccion, telefono]):
                errores.append("Todos los campos son obligatorios.")
            if not telefono.isdigit():
                errores.append("El teléfono debe contener solo números.")
            if tipo == "Empresa":
                if not cuit or not cuit.isdigit():
                    errores.append("El CUIT debe contener solo números.")

            if errores:
                st.warning("⚠️ Corrige los siguientes errores antes de continuar:")
                for err in errores:
                    st.write(f"• {err}")
            else:
                tabla = "empresa" if tipo == "Empresa" else "usuario"
                check_query = f"SELECT * FROM {tabla} WHERE mail = '{mail}'"
                existe = execute_query(check_query)

                if not existe.empty:
                    st.error("❌ Ya existe una cuenta registrada con ese correo.")
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
                        st.success("✅ Registro exitoso. Ya podés iniciar sesión.")
                        st.balloons()
                        st.markdown("""
                            <script>
                                setTimeout(function() {
                                    window.location.reload();
                                }, 3000);
                            </script>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Error al registrar. Intentá de nuevo.")

    st.markdown('</div>', unsafe_allow_html=True)

