import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query

@st.cache_data(ttl=300)  # Cache por 5 minutos
def obtener_productos_empresa(id_empresa):
    """Obtiene todos los productos de la empresa con cache"""
    query = "SELECT * FROM vista_productos_completa WHERE id_empresa = %s"
    return execute_query(query, (id_empresa,))

@st.cache_data(ttl=600)  # Cache por 10 minutos - las coberturas cambian menos
def obtener_coberturas_producto(id_producto):
    """Obtiene las coberturas de un producto específico con cache"""
    query = """
        SELECT c.nombre FROM producto_cobertura pc
        JOIN coberturas c ON pc.id_cobertura = c.id_cobertura
        WHERE pc.id_producto = %s
    """
    result = execute_query(query, (id_producto,))
    return ", ".join(result["nombre"].tolist()) if not result.empty else "Sin coberturas"

def aplicar_busqueda(df, termino_busqueda):
    """Aplica filtros de búsqueda de manera optimizada"""
    if not termino_busqueda:
        return df
    
    termino = termino_busqueda.lower()
    mask = (
        df['nombre_producto'].str.lower().str.contains(termino, na=False) |
        df['tipo'].str.lower().str.contains(termino, na=False) |
        df['material'].str.lower().str.contains(termino, na=False)
    )
    return df[mask]

def renderizar_tarjeta_producto(row, coberturas_str):
    """Renderiza una tarjeta de producto de manera optimizada"""
    peso_html = f"<p><strong>Peso:</strong> {row['peso_importado']} kg</p>" if row['peso_importado'] else ""
    
    return f"""
        <div style='background-color: #e3f2fd; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);'>
            <h4 style='margin-bottom: 0.5rem;'>{row['nombre_producto']}</h4>
            <p><strong>Tipo:</strong> {row['tipo']} | <strong>Material:</strong> {row['material']} | <strong>Precio:</strong> ${row['precio']:.2f}</p>
            {peso_html}
            <p><strong>Entrega:</strong> {row['tiempo_entrega']} días | <strong>Stock:</strong> {row['stock']}</p>
            <p>{row['descripcion']}</p>
            <p><strong>Coberturas:</strong> {coberturas_str}</p>
        </div>
    """

def eliminar_producto(id_producto):
    """Elimina un producto de manera segura"""
    try:
        query = "DELETE FROM producto WHERE id_producto = %s"
        execute_query(query, (id_producto,), is_select=False)
        return True, None
    except Exception as e:
        return False, str(e)

def mostrar():
    # Verificación temprana de empresa
    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")

    if not id_empresa:
        st.error("No se encontró la sesión de empresa.")
        return

    # Configuración de estilos solo una vez por sesión
    if "productos_styles_loaded" not in st.session_state:
        set_global_styles()
        add_page_specific_styles("empresa")
        st.session_state["productos_styles_loaded"] = True
    
    add_logo_and_header()

    st.title("Mis Productos")
    st.markdown("---")

    # Barra de búsqueda
    busqueda = st.text_input("🔍 Buscar por nombre, tipo o material:", 
                           placeholder="Ej: prótesis de pierna")

    # Cargar productos con spinner
    with st.spinner('Cargando productos...'):
        try:
            df = obtener_productos_empresa(id_empresa)
        except Exception as e:
            st.error(f"Error al cargar productos: {str(e)}")
            return

    # Aplicar búsqueda
    df_filtrado = aplicar_busqueda(df, busqueda)

    if df_filtrado.empty:
        mensaje = "No se encontraron productos que coincidan con la búsqueda." if busqueda else "No tienes productos registrados."
        st.info(mensaje)
        return

    # Paginación para mejorar performance
    productos_por_pagina = 5
    total_productos = len(df_filtrado)
    total_paginas = (total_productos - 1) // productos_por_pagina + 1

    # Control de paginación
    if total_paginas > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pagina_actual = st.selectbox(
                "Página", 
                range(1, total_paginas + 1),
                key="pagina_productos"
            )
    else:
        pagina_actual = 1

    # Calcular índices para la página actual
    inicio = (pagina_actual - 1) * productos_por_pagina
    fin = min(inicio + productos_por_pagina, total_productos)

    # Renderizar productos de la página actual
    for idx in range(inicio, fin):
        row = df_filtrado.iloc[idx]
        producto_id = row['id_producto']
        
        # Obtener coberturas con cache
        coberturas_str = obtener_coberturas_producto(producto_id)

        # Columnas: izquierda (tarjeta) - derecha (botones)
        col1, col2 = st.columns([5, 1])
        
        with col1:
            tarjeta_html = renderizar_tarjeta_producto(row, coberturas_str)
            st.markdown(tarjeta_html, unsafe_allow_html=True)

        with col2:
            st.markdown(
                "<div style='display: flex; flex-direction: column; gap: 0.5rem; padding-top: 1rem;'>",
                unsafe_allow_html=True
            )

            # Botón Editar
            if st.button("✏️ Editar", key=f"editar_{producto_id}_{pagina_actual}"):
                st.session_state["producto_a_editar"] = row.to_dict()
                st.session_state["vista"] = "editar_producto"
                st.rerun()

            # Botón Eliminar
            confirmacion_key = f"confirmar_eliminacion_{producto_id}"
            
            if st.button("🗑 Eliminar", key=f"eliminar_{producto_id}_{pagina_actual}"):
                st.session_state[confirmacion_key] = True

            # Manejo de confirmación de eliminación
            if st.session_state.get(confirmacion_key, False):
                st.warning("⚠️ ¿Estás segura/o de que quieres eliminar este producto?")

                opcion_key = f"opcion_eliminar_{producto_id}"
                opcion = st.radio(
                    "Seleccioná una opción:",
                    options=["No", "Sí"],
                    key=opcion_key,
                    horizontal=True
                )

                confirmar_key = f"confirmar_si_{producto_id}_{pagina_actual}"
                if st.button("Confirmar", key=confirmar_key):
                    if opcion == "Sí":
                        with st.spinner('Eliminando producto...'):
                            exito, error = eliminar_producto(producto_id)
                        
                        if exito:
                            # Limpiar cache después de la eliminación
                            obtener_productos_empresa.clear()
                            obtener_coberturas_producto.clear()
                            
                            st.success("✅ Producto eliminado exitosamente.")
                            
                            # Limpiar estados de confirmación
                            keys_to_remove = [k for k in st.session_state.keys() 
                                            if k.startswith(f"confirmar_eliminacion_{producto_id}") or 
                                               k.startswith(f"opcion_eliminar_{producto_id}")]
                            for key in keys_to_remove:
                                st.session_state.pop(key, None)
                            
                            st.rerun()
                        else:
                            st.error(f"❌ Error al eliminar producto: {error}")
                    else:
                        st.info("Eliminación cancelada.")
                        st.session_state.pop(confirmacion_key, None)
                        st.session_state.pop(opcion_key, None)

            st.markdown("</div>", unsafe_allow_html=True)

    # Mostrar información de paginación
    if total_paginas > 1:
        st.markdown("---")
        st.caption(f"Mostrando productos {inicio + 1}-{fin} de {total_productos}")

    # Estadísticas adicionales
    if not df.empty:
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Productos", len(df))
        with col2:
            stock_total = df['stock'].sum()
            st.metric("Stock Total", stock_total)
        with col3:
            precio_promedio = df['precio'].mean()
            st.metric("Precio Promedio", f"${precio_promedio:.2f}")
        with col4:
            productos_sin_stock = len(df[df['stock'] == 0])
            st.metric("Sin Stock", productos_sin_stock)