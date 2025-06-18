import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query
import pandas as pd
import time

@st.cache_data(ttl=300)
def obtener_productos_empresa(id_empresa):
    query = f"SELECT * FROM vista_productos_completa WHERE id_empresa = {id_empresa}"
    df = execute_query(query)
    return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

@st.cache_data(ttl=600)
def obtener_coberturas_producto(id_producto):
    query = f"""
        SELECT c.nombre FROM producto_cobertura pc
        JOIN coberturas c ON pc.id_cobertura = c.id_cobertura
        WHERE pc.id_producto = {id_producto}
    """
    result = execute_query(query)
    return ", ".join(result["nombre"].tolist()) if isinstance(result, pd.DataFrame) and not result.empty else "Sin coberturas"

def aplicar_busqueda(df, termino_busqueda):
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
    try:
        query = f"DELETE FROM producto WHERE id_producto = {id_producto}"
        execute_query(query, is_select=False)
        return True, None
    except Exception as e:
        return False, str(e)

def limpiar_cache_productos():
    """Función para limpiar todos los caches relacionados con productos"""
    obtener_productos_empresa.clear()
    obtener_coberturas_producto.clear()
    
    # IMPORTANTE: Limpiar específicamente el cache de estadísticas de empresa
    try:
        # Importar las funciones de vista_empresa para limpiar sus caches
        from views.vista_empresa import get_empresa_stats, validate_empresa_session, clear_empresa_cache
        get_empresa_stats.clear()
        validate_empresa_session.clear()
        clear_empresa_cache()
    except ImportError:
        # Si no se puede importar, intentar limpiar por session_state
        pass
    
    # Señalizar que las estadísticas necesitan actualizarse
    st.session_state['refresh_stats'] = True
    st.session_state['productos_updated_timestamp'] = time.time()
    st.session_state['force_refresh_empresa'] = True

def limpiar_estados_eliminacion(producto_id):
    """Limpia todos los estados relacionados con la eliminación de un producto específico"""
    keys_to_remove = []
    for key in st.session_state.keys():
        if (key.startswith(f"confirmar_eliminacion_{producto_id}") or 
            key.startswith(f"opcion_eliminar_{producto_id}") or
            key.startswith(f"confirmar_si_{producto_id}")):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        st.session_state.pop(key, None)

def mostrar():
    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")

    if not id_empresa:
        st.error("No se encontró la sesión de empresa.")
        return

    if "productos_styles_loaded" not in st.session_state:
        set_global_styles()
        add_page_specific_styles("empresa")
        st.session_state["productos_styles_loaded"] = True

    add_logo_and_header()

    st.title("Mis Productos")
    st.markdown("---")

    busqueda = st.text_input("🔍 Buscar por nombre, tipo o material:", placeholder="Ej: prótesis de pierna")

    with st.spinner('Cargando productos...'):
        try:
            df = obtener_productos_empresa(id_empresa)
        except Exception as e:
            st.error(f"Error al cargar productos: {str(e)}")
            return

    if not isinstance(df, pd.DataFrame):
        st.error("Error inesperado al obtener datos.")
        return

    df_filtrado = aplicar_busqueda(df, busqueda)

    if df_filtrado.empty:
        mensaje = "No se encontraron productos que coincidan con la búsqueda." if busqueda else "No tienes productos registrados."
        st.info(mensaje)
        return

    productos_por_pagina = 5
    total_productos = len(df_filtrado)
    total_paginas = (total_productos - 1) // productos_por_pagina + 1

    if total_paginas > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pagina_actual = st.selectbox("Página", range(1, total_paginas + 1), key="pagina_productos")
    else:
        pagina_actual = 1

    inicio = (pagina_actual - 1) * productos_por_pagina
    fin = min(inicio + productos_por_pagina, total_productos)

    for idx in range(inicio, fin):
        row = df_filtrado.iloc[idx]
        producto_id = row['id_producto']
        coberturas_str = obtener_coberturas_producto(producto_id)

        col1, col2 = st.columns([5, 1])
        with col1:
            tarjeta_html = renderizar_tarjeta_producto(row, coberturas_str)
            st.markdown(tarjeta_html, unsafe_allow_html=True)

        with col2:
            st.markdown("<div style='display: flex; flex-direction: column; gap: 0.5rem; padding-top: 1rem;'>", unsafe_allow_html=True)

            if st.button("✏ Editar", key=f"editar_{producto_id}_{pagina_actual}"):
                st.session_state["producto_a_editar"] = row.to_dict()
                st.session_state["vista"] = "editar_producto"
                st.rerun()

            confirmacion_key = f"confirmar_eliminacion_{producto_id}"
            if st.button("🗑 Eliminar", key=f"eliminar_{producto_id}_{pagina_actual}"):
                st.session_state[confirmacion_key] = True

            if st.session_state.get(confirmacion_key, False):
                st.warning("⚠ ¿Estás segura/o de que quieres eliminar este producto?")
                opcion_key = f"opcion_eliminar_{producto_id}"
                opcion = st.radio("Seleccioná una opción:", options=["No", "Sí"], key=opcion_key, horizontal=True)

                confirmar_key = f"confirmar_si_{producto_id}_{pagina_actual}"
                if st.button("Confirmar", key=confirmar_key):
                    if opcion == "Sí":
                        with st.spinner('Eliminando producto...'):
                            exito, error = eliminar_producto(producto_id)

                        if exito:
                            # Limpiar todos los caches y estados relacionados
                            limpiar_cache_productos()
                            limpiar_estados_eliminacion(producto_id)
                            
                            # Mostrar mensaje de éxito
                            st.success("✅ Producto eliminado exitosamente.")
                            
                            # Pequeña pausa para que el usuario vea el mensaje
                            time.sleep(0.5)
                            
                            # Rerun para actualizar la vista
                            st.rerun()
                        else:
                            st.error(f"❌ Error al eliminar producto: {error}")
                    else:
                        st.info("Eliminación cancelada.")
                        limpiar_estados_eliminacion(producto_id)
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    if total_paginas > 1:
        st.markdown("---")
        st.caption(f"Mostrando productos {inicio + 1}-{fin} de {total_productos}")

    # Agregar botón para refrescar manualmente si es necesario
    if st.button("🔄 Actualizar Lista", key="refresh_productos"):
        limpiar_cache_productos()
        st.rerun()