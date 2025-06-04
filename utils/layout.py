import streamlit as st
from PIL import Image

def set_global_styles():
    st.markdown("""
        <style>
        /* Fondo principal celeste claro */
        body, .stApp {
            background-color: #FFFFFF;
            color: #0C1F33;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #A6C9E2;
            border-right: 1px solid #3D6FA5;
        }

        /* Encabezados */
        h1, h2, h3, h4 {
            color: #0C1F33;
        }

        /* Botones */
        .stButton > button {
            background-color: #7BA7D1;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5em 1em;
            font-weight: bold;
            transition: 0.3s ease-in-out;
        }

        .stButton > button:hover {
            background-color: #6A96C0;
            transform: scale(1.05);
        }

        /* Inputs */
        input, textarea, select {
            background-color: #FFFFFF;
            border: 1px solid #0C1F33;
            color: #0C1F33;
            border-radius: 8px;
        }

        /* Tablas */
        .stDataFrame {
            border: 1px solid #3D6FA5;
            border-radius: 8px;
        }

        /* Footer */
        .custom-footer {
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid #3D6FA5;
            color: #0C1F33;
            font-size: 0.85em;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)


def add_logo_and_header():
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@700;800&display=swap" rel="stylesheet">
        <style>
            /* Header fijo mejorado */
            .sticky-header {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                width: 100%;
                background: linear-gradient(135deg, #A6C9E2 0%, #7BA7D1 100%);
                z-index: 9999;
                padding: 15px 0;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                backdrop-filter: blur(10px);
                border-bottom: 2px solid #3D6FA5;
                transition: all 0.3s ease;
            }

            .sticky-header h1 {
                margin: 0;
                font-family: 'Exo 2', sans-serif;
                font-size: 36px;
                font-weight: 800;
                color: #0C1F33;
                text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.3);
                letter-spacing: 2px;
                animation: slideDown 0.8s ease-out;
            }

            /* Animación de entrada */
            @keyframes slideDown {
                from {
                    transform: translateY(-50px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }

            /* Efecto hover en el header */
            .sticky-header:hover h1 {
                transform: scale(1.02);
                transition: transform 0.3s ease;
            }

            /* Ajuste del contenido principal */
            .stApp > div:first-child {
                padding-top: 90px !important;
            }

            /* Ocultar el header por defecto de Streamlit */
            header[data-testid="stHeader"] {
                display: none;
            }

            /* Ajustes responsivos */
            @media (max-width: 768px) {
                .sticky-header h1 {
                    font-size: 28px;
                    letter-spacing: 1px;
                }
                
                .stApp > div:first-child {
                    padding-top: 80px !important;
                }
            }

            @media (max-width: 480px) {
                .sticky-header h1 {
                    font-size: 24px;
                    letter-spacing: 0.5px;
                }
                
                .sticky-header {
                    padding: 12px 0;
                }
                
                .stApp > div:first-child {
                    padding-top: 70px !important;
                }
            }
        </style>

        <div class="sticky-header">
            <h1>PROTHESIA</h1>
        </div>
    """, unsafe_allow_html=True)


def add_footer():
    st.markdown("""
        <div class="custom-footer">
            Plataforma desarrollada por el Grupo 8: Aliaga Julieta y Chiri Julieta
        </div>
    """, unsafe_allow_html=True)


def load_css(file_path="assets/style.css"):
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Archivo CSS no encontrado: {file_path}")


def add_page_specific_styles(page_type="default"):
    """
    Agrega estilos específicos según el tipo de página
    page_type: 'login', 'empresa', 'usuario', 'registro', 'default'
    """
    if page_type == "login":
        st.markdown("""
            <style>
            /* Estilos específicos para la página de login */
            .login-container {
                max-width: 500px;
                margin: 0 auto;
                padding: 2rem;
                background-color: rgba(166, 201, 226, 0.1);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(166, 201, 226, 0.3);
            }
            
            .login-title {
                text-align: center;
                color: #0C1F33;
                margin-bottom: 2rem;
                font-weight: 700;
            }
            </style>
        """, unsafe_allow_html=True)
    
    elif page_type == "registro":
        st.markdown("""
            <style>
            /* Estilos específicos para la página de registro */
            .registro-container {
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                background-color: rgba(166, 201, 226, 0.1);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(166, 201, 226, 0.3);
            }
            
            .registro-title {
                text-align: center;
                color: #0C1F33;
                margin-bottom: 2rem;
                font-weight: 700;
            }
            
            /* Botón primario (Registrarme) - Destacado con tu color */
            .stButton > button[kind="primary"] {
                background-color: #7BA7D1 !important;
                border: none !important;
                color: white !important;
                font-weight: bold !important;
                box-shadow: 0 4px 12px rgba(123, 167, 209, 0.4) !important;
            }
            
            .stButton > button[kind="primary"]:hover {
                background-color: #6A96C0 !important;
                transform: scale(1.05) !important;
                box-shadow: 0 6px 16px rgba(123, 167, 209, 0.6) !important;
            }
            
            /* Botón secundario (Volver) - Más sutil */
            .stButton > button:not([kind="primary"]) {
                background-color: #E8E8E8 !important;
                color: #666666 !important;
                border: 1px solid #CCCCCC !important;
                font-weight: normal !important;
            }
            
            .stButton > button:not([kind="primary"]):hover {
                background-color: #D4D4D4 !important;
                color: #555555 !important;
                transform: scale(1.02) !important;
            }
            </style>
        """, unsafe_allow_html=True)
    
    elif page_type == "empresa":
        st.markdown("""
            <style>
            /* Estilos específicos para vista empresa */
            .empresa-header {
                background: linear-gradient(90deg, #A6C9E2, #7BA7D1);
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                text-align: center;
                color: #0C1F33;
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)