import streamlit as st
from PIL import Image

def set_global_styles():
    st.markdown("""
        <style>
        /* Fondo principal celeste claro */
        body, .stApp {
            background-color: #A6C9E2;
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
            background-color: #C0C0C0;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5em 1em;
            font-weight: bold;
            transition: 0.3s ease-in-out;
        }

        .stButton > button:hover {
            background-color: #2A4F78;
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
        # Cargar el logo desde la carpeta local
    logo_path = "assets/logo.png"

    # Mostrar logo alineado a la izquierda
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(logo_path, width=120)
    with col2:
        st.markdown("")  # Espacio vacío

    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@800&display=swap" rel="stylesheet">
        <style>
            .header-top {
                display: flex;
                align-items: flex-start;
                justify-content: flex-start;
                padding: 10px 30px 0 30px;
            }

            .header-top img {
                height: 90px;
            }

            .header-bar {
                background-color: #A6C9E2;
                padding: 20px;
                border-radius: 0 0 12px 12px;
                text-align: center;
                margin-top: -30px;
            }

            .header-title {
                font-family: 'Exo 2', sans-serif;
                font-size: 48px;
                font-weight: 800;
                color: #0C1F33;
                margin: 0;
            }

            .header-subtitle {
                text-align: center;
                color: white;
                margin-top: 10px;
                font-size: 18px;
            }
        </style>

        <div class="header-top">
            <img src="https://raw.githubusercontent.com/ChiriMauro/prothesia-assets/main/logo.png" />
        </div>
        <div class="header-bar">
            <div class="header-title">PROTHESIA</div>
        </div>
        <div class="header-subtitle">Conectando necesidades con soluciones</div>
    """, unsafe_allow_html=True)


def add_footer():
    st.markdown("""
        <div class="custom-footer">
            Plataforma desarrollada por el Grupo 8: Aliaga Julieta y Chiri Julieta
        </div>
    """, unsafe_allow_html=True)
