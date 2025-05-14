import streamlit as st
from functions import execute_query

st.title("Inicio de sesión - Usuario")

mail = st.text_input("Correo electrónico")
contrasena = st.text_input("Contraseña", type="password")

if st.button("Iniciar sesión"):
    if not mail or not contrasena:
        st.warning("Por favor completá todos los campos.")
    else:
        query = f"""
        SELECT * FROM usuario 
        WHERE mail = '{mail}' AND contrasena = '{contrasena}'
        """
        df = execute_query(query)
        if not df.empty:
            st.success("Inicio de sesión exitoso")
            st.session_state["usuario"] = df.iloc[0].to_dict()
        else:
            st.error("Correo o contraseña incorrectos.")
