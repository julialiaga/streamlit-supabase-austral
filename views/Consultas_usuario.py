import streamlit as st
from utils.db import execute_query
from utils.layout import set_global_styles, add_logo_and_header, add_footer

@st.cache_data(ttl=300)  # Cache por 5 minutos
def obtener_consultas_usuario(id_usuario):
    """Obtiene las consultas del usuario con cache para optimizar performance"""
    query = """
        SELECT c.id_consulta, c.fecha, c.estado_consulta, c.mensaje, 
               p.nombre AS producto, e.nombre AS empresa
        FROM consulta c
        JOIN producto p ON c.id_producto = p.id_producto
        JOIN empresa e ON c.id_empresa = e.id_empresa
        WHERE c.id_usuario = %s
        ORDER BY c.fecha DESC
    """
    return execute_query(query, (id_usuario,))

def renderizar_consulta(row):
    """Renderiza una consulta individual de manera optimizada"""
    fecha_formateada = row['fecha'].strftime('%d/%m/%Y %H:%M')
    
    return f"""
        <div style='border: 1px solid #e0e0e0; border-radius: 10px; padding: 1rem; margin-bottom: 0.5rem; background-color: #fefefe;'>
            <strong>Producto:</strong> {row['producto']}<br>
            <strong>Empresa:</strong> {row['empresa']}<br>
            <strong>Fecha:</strong> {fecha_formateada}<br>
            <strong>Consulta:</strong> {row['mensaje']}<br>
            <strong>Estado:</strong> {row['estado_consulta']}
        </div>
    """

def mostrar():
    # Verificación temprana de usuario
    usuario = st.session_state.get("usuario", {})
    if not usuario:
        st.warning("Debés iniciar sesión como usuario para ver tus consultas.")
        return

    # Configuración de estilos solo una vez
    if "styles_loaded" not in st.session_state:
        set_global_styles()
        st.session_state["styles_loaded"] = True
    
    add_logo_and_header()

    st.markdown("<h2 style='text-align:center;'>Mis Consultas Enviadas</h2>", unsafe_allow_html=True)

    id_usuario = usuario.get("id_usuario") or usuario.get("ID_usuario")
    
    # Usar spinner para feedback visual
    with st.spinner('Cargando consultas...'):
        try:
            consultas = obtener_consultas_usuario(id_usuario)
        except Exception as e:
            st.error(f"Error al cargar las consultas: {str(e)}")
            return

    if consultas.empty:
        st.info("Todavía no realizaste consultas.")
    else:
        # Paginación para mejorar performance con muchas consultas
        consultas_por_pagina = 10
        total_consultas = len(consultas)
        total_paginas = (total_consultas - 1) // consultas_por_pagina + 1
        
        # Control de paginación
        if total_paginas > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                pagina_actual = st.selectbox(
                    "Página", 
                    range(1, total_paginas + 1),
                    key="pagina_consultas"
                )
        else:
            pagina_actual = 1
        
        # Calcular índices para la página actual
        inicio = (pagina_actual - 1) * consultas_por_pagina
        fin = min(inicio + consultas_por_pagina, total_consultas)
        
        # Renderizar consultas de la página actual usando contenido HTML concatenado
        consultas_html = ""
        for index in range(inicio, fin):
            row = consultas.iloc[index]
            consultas_html += renderizar_consulta(row)
        
        # Renderizar todo el HTML de una vez
        st.markdown(consultas_html, unsafe_allow_html=True)
        
        # Mostrar información de paginación
        if total_paginas > 1:
            st.caption(f"Mostrando consultas {inicio + 1}-{fin} de {total_consultas}")

    # Botón de navegación
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Volver a la página principal", use_container_width=True):
            st.session_state["vista"] = "vista_usuario"
            st.rerun()