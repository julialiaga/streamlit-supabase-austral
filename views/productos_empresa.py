import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query


def mostrar():
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("empresa")

# Botón volver
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Volver"):
            st.session_state["vista"] = "vista_empresa"
            st.rerun()
            
    st.title("Mis Productos")
    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")

    if not id_empresa:
        st.error("No se encontró la sesión de empresa.")
        return

    

    st.markdown("---")

    # Filtros
    st.subheader("Filtros")
    tipos = execute_query("SELECT DISTINCT tipo FROM producto")
    materiales = execute_query("SELECT DISTINCT material FROM producto")

    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        tipo_filtro = st.selectbox("Tipo", ["Todos"] + sorted(tipos["tipo"].dropna().tolist()))
    with colf2:
        material_filtro = st.selectbox("Material", ["Todos"] + sorted(materiales["material"].dropna().tolist()))
    with colf3:
        precio_min = st.number_input("Precio mínimo", min_value=0.0, step=100.0, format="%.2f")
    with colf4:
        solo_stock = st.checkbox("Solo con stock disponible")

    # Consulta base
    query = f"SELECT * FROM vista_productos_completa WHERE id_empresa = {id_empresa}"
    df = execute_query(query)

    if tipo_filtro != "Todos":
        df = df[df["tipo"] == tipo_filtro]
    if material_filtro != "Todos":
        df = df[df["material"] == material_filtro]
    df = df[df["precio"] >= precio_min]
    if solo_stock:
        df = df[df["stock"] > 0]

    if df.empty:
        st.info("No se encontraron productos con los filtros aplicados.")
        return

    st.markdown("---")

    # Tarjetas de productos
    for i, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {row['nombre_producto']}")
                st.markdown(f"**Tipo:** {row['tipo']} | **Material:** {row['material']} | **Precio:** ${row['precio']:.2f}")
                if row['peso_importado']:
                    st.markdown(f"**Peso:** {row['peso_importado']} kg")
                st.markdown(f"**Entrega:** {row['tiempo_entrega']} días | **Stock:** {row['stock']}")

                # Descripción con leer más
                if len(row['descripcion']) > 120:
                    with st.expander("📝 Leer más"):
                        st.write(row['descripcion'])
                else:
                    st.write(row['descripcion'])

                # Coberturas asociadas
                query_coberturas = f"""
                    SELECT c.nombre FROM producto_cobertura pc
                    JOIN coberturas c ON pc.id_cobertura = c.id_cobertura
                    WHERE pc.id_producto = {row['id_producto']}
                """
                coberturas = execute_query(query_coberturas)
                if not coberturas.empty:
                    st.markdown("**Coberturas:** " + ", ".join(coberturas["nombre"].tolist()))

            with col2:
                if st.button("✏️ Editar", key=f"editar_{i}"):
                    st.session_state["producto_a_editar"] = row.to_dict()
                    st.session_state["vista"] = "Editar_producto"
                    st.rerun()

                if st.button("🗑 Eliminar", key=f"eliminar_{i}"):
                    if st.confirm(f"¿Estás segura de que querés eliminar el producto '{row['nombre_producto']}'?"):
                        try:
                            eliminar_query = f"DELETE FROM producto WHERE id_producto = {row['id_producto']}"
                            execute_query(eliminar_query, is_select=False)
                            st.success("Producto eliminado exitosamente.")
                            st.rerun()
                        except Exception as e:
                            st.error("Error al eliminar producto: " + str(e))

