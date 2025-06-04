import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query

def mostrar():
    # Aplicar estilos específicos para la página de registro
    add_page_specific_styles("registro")
    
    # Contenedor principal con estilo
    
    st.markdown('<h2 class="registro-title">Registro de Cuenta</h2>', unsafe_allow_html=True)
    
    # Espaciado
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Selector de tipo de usuario
    tipo = st.selectbox(" ¿Te registrás como?", ["Usuario", "Empresa"], 
                       help="Selecciona el tipo de cuenta que deseas crear")
    
    # Espaciado
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Campos del formulario con iconos
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("Nombre", placeholder="Ingresa tu nombre completo")
        mail = st.text_input("Correo electrónico", placeholder="ejemplo@correo.com")
        contrasena = st.text_input("Contraseña", type="password", placeholder="Crea una contraseña segura")
    
    with col2:
        direccion = st.text_input("Dirección", placeholder="Calle, número, ciudad")
        telefono = st.text_input("Teléfono", placeholder="Solo números (ej: 1123456789)")
        
        # Campo CUIT solo para empresas
        if tipo == "Empresa":
            cuit = st.text_input("CUIT", placeholder="Solo números (ej: 20123456789)")
        else:
            cuit = None
    
    # Espaciado
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botones
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn1:
        if st.button("⬅ Volver al Login", use_container_width=True):
            st.session_state["vista"] = "inicio"
            st.rerun()
    
    with col_btn2:
        # Espaciado visual
        st.markdown("")
    
    with col_btn3:
        if st.button("Registrarme", use_container_width=True, type="primary"):
            # Validaciones
            if not nombre or not mail or not contrasena or not direccion or not telefono:
                st.warning("⚠️ Por favor completá todos los campos obligatorios.")
            elif tipo == "Empresa" and (not cuit or not cuit.isdigit()):
                st.warning("⚠️ El CUIT debe contener solo números.")
            elif not telefono.isdigit():
                st.warning("⚠️ El teléfono debe contener solo números.")
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
                            VALUES ('{nombre}', '{mail}', '{contrasena}', '{direccion}', '{telefono}', '{cuit}')
                        """
                    else:
                        insert_query = f"""
                            INSERT INTO usuario (nombre, mail, contrasena, direccion, telefono)
                            VALUES ('{nombre}', '{mail}', '{contrasena}', '{direccion}', '{telefono}')
                        """

                    # Ejecutar el insert
                    try:
                        execute_query(insert_query)
                        st.success("Registro exitoso. Ya podés iniciar sesión.")
                        st.balloons()  # Efecto visual de celebración
                        
                        # Auto-redirigir después de 2 segundos
                        st.markdown("""
                            <script>
                            setTimeout(function() {
                                window.location.reload();
                            }, 3000);
                            </script>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"❌ Ocurrió un error durante el registro: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar contenedor
    
    # Información adicional
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #0C1F33; font-size: 0.9em; margin-top: 1rem;'>
            <p> 🔒 Tu información está protegida y no será compartida con terceros</p>
        </div>
    """, unsafe_allow_html=True)