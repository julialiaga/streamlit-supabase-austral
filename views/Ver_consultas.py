import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query
import pandas as pd

@st.cache_data(ttl=180)
def obtener_consultas(id_empresa):
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
    return execute_query(query)

def mostrar():
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("empresa")

    st.title("Consultas Recibidas")
    st.markdown("---")

    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")

    if not id_empresa:
        st.error("⚠️ No se encontró la sesión de empresa.")
        return

    df = obtener_consultas(id_empresa)

    if df.empty:
        st.info("No tenés consultas por el momento.")
        return

    df["fecha_formateada"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y %H:%M")
    pendientes = df[df['estado_consulta'] == 'Pendiente']
    respondidas = df[df['estado_consulta'] != 'Pendiente']

    def render_consulta(row, responder=False):
        with st.container():
            st.markdown(f"### 💬 Producto: {row['nombre_producto']}")
            st.markdown(f"**👤 Usuario:** {row['nombre_usuario']} | ✉️ {row['mail_usuario']}")
            st.markdown(f"📅 Fecha: {row['fecha_formateada']}")
            st.markdown(f"🟢 Estado: `{row['estado_consulta']}`")

            mensaje = row['mensaje']
            if len(mensaje) > 200:
                with st.expander("📩 Ver mensaje completo"):
                    st.markdown(mensaje)
            else:
                st.markdown(f"**Mensaje:** {mensaje}")

            if responder:
                respuesta_key = f"respuesta_{row['id_consulta']}"
                respuesta = st.text_area("✏️ Responder:", key=respuesta_key, placeholder="Escribí aquí tu respuesta...")

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
                            obtener_consultas.clear()
                            st.success("✅ Respuesta enviada correctamente.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al guardar la respuesta: {e}")
            st.markdown("---")

    # Mostrar pendientes
    st.markdown("<h3 style='color: #2c5282;'> Consultas Pendientes</h3>", unsafe_allow_html=True)
    if not pendientes.empty:
        for _, row in pendientes.iterrows():
            render_consulta(row, responder=True)
    else:
        st.info("No tenés consultas pendientes.")

    # Mostrar respondidas
    st.markdown("<h3 style='color: #2c5282;'> Consultas Respondidas</h3>", unsafe_allow_html=True)
    if not respondidas.empty:
        for _, row in respondidas.iterrows():
            render_consulta(row)
