import streamlit as st
from utils.db import execute_query
from utils.layout import set_global_styles, add_logo_and_header, add_footer

def mostrar():
    set_global_styles()
    add_logo_and_header()

    st.markdown("<h2 style='text-align:center;'>Mis Consultas Enviadas</h2>", unsafe_allow_html=True)

    usuario = st.session_state.get("usuario", {})
    if not usuario:
        st.warning("Debés iniciar sesión como usuario para ver tus consultas.")
        return

    id_usuario = usuario.get("id_usuario") or usuario.get("ID_usuario")

    query = f"""
        SELECT c.fecha, c.estado_consulta, c.mensaje, p.nombre AS producto, e.nombre AS empresa
        FROM consulta c
        JOIN producto p ON c.id_producto = p.id_producto
        JOIN empresa e ON c.id_empresa = e.id_empresa
        WHERE c.id_usuario = {id_usuario}
        ORDER BY c.fecha DESC
    """

    consultas = execute_query(query)

    if consultas.empty:
        st.info("Todavía no realizaste consultas.")
    else:
        for _, row in consultas.iterrows():
            with st.container():
                st.markdown(f"""
                    <div style='border: 1px solid #e0e0e0; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; background-color: #fefefe;'>
                        <strong> Producto:</strong> {row['producto']}  
                        <br><strong> Empresa:</strong> {row['empresa']}  
                        <br><strong> Fecha:</strong> {row['fecha'].strftime('%d/%m/%Y %H:%M')}  
                        <br><strong> Consulta:</strong> {row['mensaje']}  
                        <br><strong> Estado:</strong> {row['estado_consulta']}
                    </div>
                """, unsafe_allow_html=True)

    if st.button("⬅ Volver", use_container_width=True):
        st.session_state["vista"] = "vista_usuario"
        st.rerun()