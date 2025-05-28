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
            background-color: #A6C9E2;
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
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@800&display=swap" rel="stylesheet">
        <style>
            /* Franja fija arriba */
            .sticky-header {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                background-color: #A6C9E2;
                z-index: 9999;
                padding: 20px 0;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }

            .sticky-header h1 {
                margin: 0;
                position: relative;
                top: 22px;  /* 👈 Esto baja solo el texto sin modificar la altura de la franja */
                font-family: 'Exo 2', sans-serif;
                font-size: 40px;
                font-weight: 800;
                color: #0C1F33;
            }


            /* Agrega espacio arriba al contenido para que no quede tapado */
            .stApp {
                padding-top: 100px !important;
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
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
