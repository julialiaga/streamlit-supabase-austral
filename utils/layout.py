import streamlit as st

def set_background_color(hex_color="#0F172A"):
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {hex_color} !important;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #A5D8FF !important;
        }}
        p, label, div, span {{
            color: #F8FAFC !important;
        }}
        .stButton>button {{
            background-color: #3B82F6;
            color: white;
        }}
        .stTextInput>div>input {{
            background-color: #1E293B;
            color: white;
        }}
    </style>
    """, unsafe_allow_html=True)

def add_logo_and_header():
    logo_url = "https://i.ibb.co/PmpxW0m/logo.png"
    st.image("assets/logo.png", width=120)
    st.markdown("<h1 style='text-align: center; color: #60A5FA;'>PROTHESIA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #F8FAFC;'>Conectando necesidades con soluciones</p>", unsafe_allow_html=True)

def add_footer():
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>© 2025 PROTHESIA - Todos los derechos reservados.</p>", unsafe_allow_html=True)
