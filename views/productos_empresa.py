import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query

def mostrar():
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("empresa")

    st.title("Mis Productos")
    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")

    if not id_empresa:
        st.error("No se encontró la sesión de empresa.")
        return

    st.markdown("---")

    # Barra de búsqueda
    busqueda = st.text_input("🔍 Buscar por nombre, tipo o material:", placeholder="Ej: prótesis de pierna")

    # Consulta base
    query = f"SELECT * FROM vista_productos_completa WHERE id_empresa = {id_empresa}"
    df = execute_query(query)

    if busqueda:
        busqueda = busqueda.lower()
        df = df[df.apply(lambda row: busqueda in str(row['nombre_producto']).lower() or 
                                        busqueda in str(row['tipo']).lower() or 
                                        busqueda in str(row['material']).lower(), axis=1)]

    if df.empty:
        st.info("No se encontraron productos que coincidan con la búsqueda.")
        return

    # Tarjetas de productos
    for i, row in df.iterrows():
        # Traer coberturas
        query_coberturas = f"""
            SELECT c.nombre FROM producto_cobertura pc
            JOIN coberturas c ON pc.id_cobertura = c.id_cobertura
            WHERE pc.id_producto = {row['id_producto']}
        """
        coberturas = execute_query(query_coberturas)
        coberturas_str = ", ".join(coberturas["nombre"].tolist()) if not coberturas.empty else "Sin coberturas"

        # Columnas: izquierda (tarjeta) - derecha (botones)
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
                <div style='background-color: #e3f2fd; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.1);'>
                    <h4 style='margin-bottom: 0.5rem;'>{row['nombre_producto']}</h4>
                    <p><strong>Tipo:</strong> {row['tipo']} | <strong>Material:</strong> {row['material']} | <strong>Precio:</strong> ${row['precio']:.2f}</p>
                    {f"<p><strong>Peso:</strong> {row['peso_importado']} kg</p>" if row['peso_importado'] else ""}
                    <p><strong>Entrega:</strong> {row['tiempo_entrega']} días | <strong>Stock:</strong> {row['stock']}</p>
                    <p>{row['descripcion']}</p>
                    <p><strong>Coberturas:</strong> {coberturas_str}</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(
                "<div style='display: flex; flex-direction: column; gap: 0.5rem; padding-top: 1rem;'>",
                unsafe_allow_html=True
            )

            if st.button("✏️ Editar", key=f"editar_{i}"):
                st.session_state["producto_a_editar"] = row.to_dict()
                st.session_state["vista"] = "editar_producto"
                st.rerun()

            # Botón Eliminar
            if st.button("🗑 Eliminar", key=f"eliminar_{i}"):
                st.session_state[f"confirmar_eliminacion_{i}"] = True

            # Si se activó la eliminación, mostrar opciones
            if st.session_state.get(f"confirmar_eliminacion_{i}", False):
                st.warning("⚠️ ¿Estás segura/o de que quieres eliminar este producto?")

                opcion = st.radio(
                    "Seleccioná una opción:",
                    options=["No", "Sí"],
                    key=f"opcion_eliminar_{i}",
                    horizontal=True
                )

                if st.button("Confirmar", key=f"confirmar_si_{i}"):
                    if opcion == "Sí":
                        try:
                            eliminar_query = f"DELETE FROM producto WHERE id_producto = {row['id_producto']}"
                            execute_query(eliminar_query, is_select=False)
                            st.success("Producto eliminado exitosamente.")
                            st.session_state.pop(f"confirmar_eliminacion_{i}", None)
                            st.rerun()
                        except Exception as e:
                            st.error("❌ Error al eliminar producto: " + str(e))
                    else:
                        st.info("Eliminación cancelada.")
                        st.session_state.pop(f"confirmar_eliminacion_{i}", None)


            st.markdown("</div>", unsafe_allow_html=True)


