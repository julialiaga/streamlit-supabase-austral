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

    # Mostrar pendientes
    if not pendientes.empty:
        st.markdown("<h3 style='color: #2C5282;'>Consultas Pendientes</h3>", unsafe_allow_html=True)
        for _, row in pendientes.iterrows():
            with st.container():
                st.markdown(f"### 💬 Producto: {row['nombre_producto']}")
                st.markdown(f"**👤 Usuario:** {row['nombre_usuario']} | ✉️ {row['mail_usuario']}")
                st.markdown(f"📅 Fecha: {pd.to_datetime(row['fecha']).strftime('%d/%m/%Y %H:%M')}")
                st.markdown(f"🟢 Estado: `{row['estado_consulta']}`")

                # Mensaje
                mensaje = row['mensaje']
                if len(mensaje) > 200:
                    with st.expander("📩 Ver mensaje completo"):
                        st.markdown(mensaje)
                else:
                    st.markdown(f"**Mensaje:** {mensaje}")

                # Campo para responder
                respuesta_clave = f"respuesta_{row['id_consulta']}"
                respuesta = st.text_area("Responder:", key=respuesta_clave, placeholder="Escribí aquí tu respuesta...")

                if st.button("📨 Enviar respuesta", key=f"enviar_{row['id_consulta']}"):
                    if not respuesta.strip():
                        st.warning("No podés enviar una respuesta vacía.")
                    else:
                        try:
                            update_query = f"""
                                UPDATE consulta
                                SET estado_consulta = 'Respondida'
                                WHERE id_consulta = {row['id_consulta']}
                            """
                            execute_query(update_query, is_select=False)
                            st.success("Respuesta enviada correctamente.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al guardar la respuesta: {e}")
                st.markdown("---")
    else:
        st.info("No tenés consultas pendientes.")

    # Mostrar las respondidas
    if not otras.empty:
        st.markdown("<h3 style='color: #2C5282;'>Consultas Respondidas</h3>", unsafe_allow_html=True)
        for _, row in otras.iterrows():
            with st.container():
                st.markdown(f"### 💬 Producto: {row['nombre_producto']}")
                st.markdown(f"**👤 Usuario:** {row['nombre_usuario']} | ✉️ {row['mail_usuario']}")
                st.markdown(f"📅 Fecha: {pd.to_datetime(row['fecha']).strftime('%d/%m/%Y %H:%M')}")
                st.markdown(f"🟢 Estado: `{row['estado_consulta']}`")
                mensaje = row['mensaje']
                if len(mensaje) > 200:
                    with st.expander("📩 Ver mensaje completo"):
                        st.markdown(mensaje)
                else:
                    st.markdown(f"**Mensaje:** {mensaje}")
                st.markdown("---")
