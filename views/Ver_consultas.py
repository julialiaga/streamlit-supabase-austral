import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query
import pandas as pd

def mostrar():
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("empresa")

    st.markdown("## Consultas Recibidas")
    st.markdown("---")

    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Volver"):
            st.session_state["vista"] = "vista_empresa"
            st.rerun()

    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")

    if not id_empresa:
        st.error("⚠️ No se encontró la sesión de empresa.")
        return

    # Obtener todas las consultas recibidas por esta empresa
    query = f"""
        SELECT c.id_consulta, c.mensaje, c.fecha, c.estado_consulta,
               u.nombre AS nombre_usuario, u.mail AS mail_usuario,
               p.nombre AS nombre_producto
        FROM consulta c
        JOIN usuario u ON c.id_usuario = u.id_usuario
        JOIN producto p ON c.id_producto = p.id_producto
        WHERE c.id_empresa = {id_empresa}
        ORDER BY 
            CASE WHEN c.estado_consulta = 'Pendiente' THEN 0 ELSE 1 END,
            c.fecha DESC;
    """
    df = execute_query(query)

    if df.empty:
        st.info("No tenés consultas por el momento.")
        return

    # Separar en dos bloques: pendientes y respondidas/cerradas
    pendientes = df[df['estado_consulta'] == 'Pendiente']
    otras = df[df['estado_consulta'] != 'Pendiente']

    def mostrar_tarjeta(row):
        with st.container():
            st.markdown(f"### 💬 Producto: {row['nombre_producto']}")
            st.markdown(f"**👤 Usuario:** {row['nombre_usuario']} | ✉️ {row['mail_usuario']}")
            st.markdown(f"📅 Fecha: {pd.to_datetime(row['fecha']).strftime('%d/%m/%Y %H:%M')}")
            st.markdown(f"🟢 Estado: `{row['estado_consulta']}`")

            # Texto del mensaje
            mensaje = row['mensaje']
            if len(mensaje) > 200:
                with st.expander("📩 Ver mensaje completo"):
                    st.markdown(mensaje)
            else:
                st.markdown(f"**Mensaje:** {mensaje}")
            
            st.markdown("---")

    # Mostrar pendientes
    if not pendientes.empty:
        st.subheader("🔴 Consultas Pendientes")
        for _, row in pendientes.iterrows():
            mostrar_tarjeta(row)
    else:
        st.info("No tenés consultas pendientes.")

    # Mostrar las otras
    if not otras.empty:
        st.subheader("📁 Consultas Respondidas / Cerradas")
        for _, row in otras.iterrows():
            mostrar_tarjeta(row)
