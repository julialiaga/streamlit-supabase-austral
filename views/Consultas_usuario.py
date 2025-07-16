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

    # Modificar la query para incluir la respuesta
    query = f"""
        SELECT c.fecha, c.estado_consulta, c.mensaje, c.respuesta,
               p.nombre AS producto, e.nombre AS empresa
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
                # Determinar el color del borde según el estado
                if row['estado_consulta'] == 'Respondida':
                    border_color = '#4CAF50'  # Verde para respondidas
                    bg_color = '#f8fff8'
                elif row['estado_consulta'] == 'Pendiente':
                    border_color = '#FFC107'  # Amarillo para pendientes
                    bg_color = '#fffef8'
                else:
                    border_color = '#e0e0e0'  # Gris por defecto
                    bg_color = '#fefefe'

                st.markdown(f"""
                    <div style='border: 2px solid {border_color}; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; background-color: {bg_color};'>
                        <strong>📦 Producto:</strong> {row['producto']}  
                        <br><strong>🏢 Empresa:</strong> {row['empresa']}  
                        <br><strong>📅 Fecha:</strong> {row['fecha'].strftime('%d/%m/%Y %H:%M')}  
                        <br><strong>💬 Consulta:</strong> {row['mensaje']}  
                        <br><strong>📊 Estado:</strong> <span style='color: {"green" if row["estado_consulta"] == "Respondida" else "orange"};'>{row['estado_consulta']}</span>
                """, unsafe_allow_html=True)
                
                # Mostrar la respuesta si existe
                if row['estado_consulta'] == 'Respondida' and row['respuesta']:
                    st.markdown(f"""
                        <div style='margin-top: 1rem; padding: 1rem; background-color: #e8f5e8; border-left: 4px solid #4CAF50; border-radius: 5px;'>
                            <strong>✅ Respuesta de la empresa:</strong><br>
                            {row['respuesta']}
                        </div>
                    """, unsafe_allow_html=True)
                elif row['estado_consulta'] == 'Pendiente':
                    st.markdown(f"""
                        <div style='margin-top: 1rem; padding: 1rem; background-color: #fff3cd; border-left: 4px solid #FFC107; border-radius: 5px;'>
                            <strong>⏳ Tu consulta está pendiente de respuesta</strong>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

    if st.button("⬅ Volver", use_container_width=True):
        st.session_state["vista"] = "vista_usuario"
        st.rerun()