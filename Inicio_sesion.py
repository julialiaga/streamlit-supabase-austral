import streamlit as st
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from utils.layout import set_global_styles, add_logo_and_header, add_footer, load_css, add_page_specific_styles
from utils.db import execute_query

st.set_page_config(page_title="Prothesia", page_icon="🦾", layout="centered")
load_css("assets/style.css")

# Inicializar estados
if "tipo_login" not in st.session_state:
    st.session_state.tipo_login = None

if "vista" not in st.session_state:
    st.session_state["vista"] = "inicio"

# Estética general
set_global_styles()
add_logo_and_header()
add_page_specific_styles("login")  # Estilos específicos para login

# VISTA INICIO
if st.session_state["vista"] == "inicio":
    # Contenedor principal con estilo
    
    
    st.markdown('<h2 class="login-title">¿Cómo quieres ingresar?</h2>', unsafe_allow_html=True)
    
    # Espaciado
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Botones centrados y con mejor estilo
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("👤 Usuario", use_container_width=True):
                st.session_state.tipo_login = "usuario"
        
        with col_btn2:
            if st.button("🏢 Empresa", use_container_width=True):
                st.session_state.tipo_login = "empresa"
    
    # Formulario de login
    if st.session_state.tipo_login:
        tipo = st.session_state.tipo_login
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"### Inicio de sesión - {tipo.capitalize()}", unsafe_allow_html=True)
        
        # Espaciado
        st.markdown("<br>", unsafe_allow_html=True)
        
        correo = st.text_input("Correo electrónico", key="mail_" + tipo, placeholder="ejemplo@correo.com")
        contrasena = st.text_input("Contraseña", type="password", key="pass_" + tipo, placeholder="Ingresa tu contraseña")
        
        # Espaciado
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
        
        with col_login2:
            if st.button("Iniciar sesión", use_container_width=True):
                if not correo or not contrasena:
                    st.warning("⚠️ Por favor completá todos los campos.")
                else:
                    tabla = "usuario" if tipo == "usuario" else "empresa"
                    query = f"SELECT * FROM {tabla} WHERE mail = '{correo}' AND contrasena = '{contrasena}'"
                    resultado = execute_query(query)
                    
                    if not resultado.empty:
                        st.success("Inicio de sesión exitoso.")
                        st.session_state[tipo] = resultado.iloc[0].to_dict()
                        
                        # Redirigir según el tipo de login
                        if tipo == "empresa":
                            st.session_state["vista"] = "vista_empresa"  # CAMBIO AQUÍ
                            st.rerun()
                        elif tipo == "usuario":
                            st.session_state["vista"] = "vista_usuario"
                            st.rerun()
                    else:
                        st.error("❌ Correo o contraseña incorrectos.")
        
        # Botón de volver más sutil
        #if st.button("⬅ Volver", help="Volver a la selección de tipo de usuario"):
        #    st.session_state.tipo_login = None
        #    st.rerun()
    
    # Enlace a registro
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #0C1F33;'>¿No estás registrado?</p>", unsafe_allow_html=True)
    
    col_reg = st.columns([1, 2, 1])
    with col_reg[1]:
        if st.button("Ir a registro", use_container_width=True):
            st.session_state["vista"] = "registro"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar contenedor

# VISTA REGISTRO
elif st.session_state["vista"] == "registro":
    from views import Registro
    Registro.mostrar()

# VISTA EMPRESA (redireccionada desde login)
elif st.session_state["vista"] == "vista_empresa":  # CAMBIO AQUÍ
    from views import Vista_empresa
    Vista_empresa.mostrar()

# CARGAR PRODUCTO
elif st.session_state["vista"] == "Cargar_producto":
    from views import Cargar_producto
    Cargar_producto.mostrar()

# VISTA PRODUCTOS DE EMPRESA
elif st.session_state["vista"] == "productos_empresa":
    from views import productos_empresa
    productos_empresa.mostrar()


# VER CONSULTAS
elif st.session_state["vista"] == "Ver_consultas":
    from views import Ver_consultas
    Ver_consultas.mostrar()

# VISTA USUARIO
elif st.session_state["vista"] == "vista_usuario":
    from views import Vista_usuario
    Vista_usuario.mostrar()

# VISTA CONSULTAS USUARIO
elif st.session_state["vista"] == "consultas_usuario":
    from views import Consultas_usuario
    Consultas_usuario.mostrar()


add_footer()