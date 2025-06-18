import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query
import pandas as pd

@st.cache_data(ttl=180)  # Cache por 3 minutos (consultas cambian frecuentemente)
def obtener_consultas_empresa(id_empresa):
    """Obtiene todas las consultas de la empresa con cache"""
    query = """
        SELECT c.id_consulta, c.mensaje, c.fecha, c.estado_consulta,
               u.nombre AS nombre_usuario, u.mail AS mail_usuario,
               p.nombre AS nombre_producto
        FROM consulta c
        JOIN usuario u ON c.id_usuario = u.id_usuario
        JOIN producto p ON c.id_producto = p.id_producto
        WHERE c.id_empresa = %s
        ORDER BY 
            CASE WHEN c.estado_consulta = 'Pendiente' THEN 0 ELSE 1 END,
            c.fecha DESC
    """
    return execute_query(query, (id_empresa,))

def procesar_consultas(df):
    """Procesa y separa las consultas en pendientes y otras"""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # Convertir fecha una sola vez
    df['fecha_formateada'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
    
    pendientes = df[df['estado_consulta'] == 'Pendiente'].copy()
    otras = df[df['estado_consulta'] != 'Pendiente'].copy()
    
    return pendientes, otras

def renderizar_consulta_base(row, mostrar_respuesta=False):
    """Renderiza el contenido base de una consulta"""
    mensaje = row['mensaje']
    mensaje_html = ""
    
    if len(mensaje) > 200:
        mensaje_preview = mensaje[:200] + "..."
        mensaje_html = f"""
            <div style='background-color: #f8f9fa; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0;'>
                <strong>Mensaje:</strong> {mensaje_preview}
                <br><small style='color: #666;'>📩 Mensaje completo disponible al expandir</small>
            </div>
        """
    else:
        mensaje_html = f"""
            <div style='background-color: #f8f9fa; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0;'>
                <strong>Mensaje:</strong> {mensaje}
            </div>
        """
    
    estado_color = "#28a745" if row['estado_consulta'] == 'Pendiente' else "#6c757d"
    
    return f"""
        <div style='border: 1px solid #e9ecef; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; background-color: white;'>
            <h4 style='margin-bottom: 0.5rem; color: #2C5282;'>💬 Producto: {row['nombre_producto']}</h4>
            <p style='margin: 0.25rem 0;'><strong>👤 Usuario:</strong> {row['nombre_usuario']} | <strong>✉️</strong> {row['mail_usuario']}</p>
            <p style='margin: 0.25rem 0;'><strong>📅 Fecha:</strong> {row['fecha_formateada']}</p>
            <p style='margin: 0.25rem 0;'><strong>🟢 Estado:</strong> <span style='color: {estado_color}; font-weight: bold;'>{row['estado_consulta']}</span></p>
            {mensaje_html}
        </div>
    """

def responder_consulta(id_consulta, respuesta):
    """Responde a una consulta y actualiza su estado"""
    try:
        query = "UPDATE consulta SET estado_consulta = 'Respondida' WHERE id_consulta = %s"
        execute_query(query, (id_consulta,), is_select=False)
        return True, None
    except Exception as e:
        return False, str(e)

def mostrar_consultas_pendientes(pendientes):
    """Muestra las consultas pendientes con formularios de respuesta"""
    if pendientes.empty:
        st.info("No tenés consultas pendientes.")
        return
    
    st.markdown("<h3 style='color: #2C5282;'>Consultas Pendientes</h3>", unsafe_allow_html=True)
    
    for _, row in pendientes.iterrows():
        # Renderizar contenido base
        consulta_html = renderizar_consulta_base(row, mostrar_respuesta=True)
        st.markdown(consulta_html, unsafe_allow_html=True)
        
        # Mostrar mensaje completo si es necesario
        if len(row['mensaje']) > 200:
            with st.expander("📩 Ver mensaje completo"):
                st.markdown(row['mensaje'])
        
        # Formulario de respuesta
        with st.form(key=f"form_respuesta_{row['id_consulta']}"):
            respuesta = st.text_area(
                "Responder:", 
                key=f"respuesta_{row['id_consulta']}", 
                placeholder="Escribí aquí tu respuesta...",
                height=100
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                submitted = st.form_submit_button("📨 Enviar respuesta", type="primary")
            
            if submitted:
                if not respuesta.strip():
                    st.warning("⚠️ No podés enviar una respuesta vacía.")
                else:
                    with st.spinner('Enviando respuesta...'):
                        exito, error = responder_consulta(row['id_consulta'], respuesta)
                    
                    if exito:
                        # Limpiar cache para refrescar los datos
                        obtener_consultas_empresa.clear()
                        st.success("✅ Respuesta enviada correctamente.")
                        st.rerun()
                    else:
                        st.error(f"❌ Error al enviar la respuesta: {error}")
        
        st.markdown("---")

def mostrar_consultas_respondidas(otras):
    """Muestra las consultas respondidas con paginación"""
    if otras.empty:
        return
    
    st.markdown("<h3 style='color: #2C5282;'>Consultas Respondidas</h3>", unsafe_allow_html=True)
    
    # Paginación para consultas respondidas
    consultas_por_pagina = 5
    total_consultas = len(otras)
    total_paginas = (total_consultas - 1) // consultas_por_pagina + 1
    
    if total_paginas > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pagina_actual = st.selectbox(
                "Página de consultas respondidas", 
                range(1, total_paginas + 1),
                key="pagina_respondidas"
            )
    else:
        pagina_actual = 1
    
    # Calcular índices para la página actual
    inicio = (pagina_actual - 1) * consultas_por_pagina
    fin = min(inicio + consultas_por_pagina, total_consultas)
    
    # Renderizar consultas de la página actual
    consultas_html = ""
    for idx in range(inicio, fin):
        row = otras.iloc[idx]
        consulta_html = renderizar_consulta_base(row)
        consultas_html += consulta_html
        
        # Agregar expansor para mensajes largos
        if len(row['mensaje']) > 200:
            consultas_html += f"<p><small>📩 <em>Mensaje completo disponible al expandir</em></small></p>"
    
    # Renderizar todas las consultas de una vez
    st.markdown(consultas_html, unsafe_allow_html=True)
    
    # Expandir mensajes largos individualmente
    for idx in range(inicio, fin):
        row = otras.iloc[idx]
        if len(row['mensaje']) > 200:
            with st.expander(f"📩 Ver mensaje completo - {row['nombre_producto']}"):
                st.markdown(row['mensaje'])
    
    # Mostrar información de paginación
    if total_paginas > 1:
        st.caption(f"Mostrando consultas {inicio + 1}-{fin} de {total_consultas}")

def mostrar():
    # Verificación temprana de empresa
    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")

    if not id_empresa:
        st.error("⚠️ No se encontró la sesión de empresa.")
        return

    # Configuración de estilos solo una vez por sesión
    if "consultas_styles_loaded" not in st.session_state:
        set_global_styles()
        add_page_specific_styles("empresa")
        st.session_state["consultas_styles_loaded"] = True
    
    add_logo_and_header()

    st.markdown("## Consultas Recibidas")
    st.markdown("---")

    # Cargar consultas con spinner
    with st.spinner('Cargando consultas...'):
        try:
            df = obtener_consultas_empresa(id_empresa)
        except Exception as e:
            st.error(f"Error al cargar las consultas: {str(e)}")
            return

    if df.empty:
        st.info("No tenés consultas por el momento.")
        return

    # Procesar consultas
    pendientes, otras = procesar_consultas(df)

    # Mostrar estadísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Consultas", len(df))
    with col2:
        st.metric("Pendientes", len(pendientes))
    with col3:
        st.metric("Respondidas", len(otras))

    st.markdown("---")

    # Mostrar consultas pendientes
    mostrar_consultas_pendientes(pendientes)

    # Mostrar consultas respondidas
    if not otras.empty:
        mostrar_consultas_respondidas(otras)