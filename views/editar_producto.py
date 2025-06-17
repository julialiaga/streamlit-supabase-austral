import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query

def mostrar():
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("empresa")

    st.markdown('<h2 class="registro-title">Editar Producto</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    producto = st.session_state.get("producto_a_editar", {})
    if not producto:
        st.error("No se encontró el producto a editar.")
        return

    id_producto = producto.get("id_producto")

    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Volver"):
            st.session_state["vista"] = "vista_empresa"
            st.rerun()

    st.markdown("---")

    # Obtener coberturas disponibles y actuales
    coberturas_df = execute_query("SELECT * FROM coberturas ORDER BY nombre")
    actuales_df = execute_query(f"SELECT id_cobertura FROM producto_cobertura WHERE id_producto = {id_producto}")
    coberturas_actuales = actuales_df["id_cobertura"].tolist() if not actuales_df.empty else []

    with st.form("form_editar_producto"):
        st.markdown("### Información del Producto")

        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del producto *", value=producto["nombre_producto"])
        with col2:
            tipo = st.selectbox("Tipo de prótesis *", [
                "Prótesis de miembro superior",
                "Prótesis de miembro inferior",
                "Prótesis de mano",
                "Prótesis de pie",
                "Prótesis facial",
                "Prótesis dental",
                "Otras"
            ], index=0 if producto["tipo"] not in [
                "Prótesis de miembro superior",
                "Prótesis de miembro inferior",
                "Prótesis de mano",
                "Prótesis de pie",
                "Prótesis facial",
                "Prótesis dental",
                "Otras"
            ] else [
                "Prótesis de miembro superior",
                "Prótesis de miembro inferior",
                "Prótesis de mano",
                "Prótesis de pie",
                "Prótesis facial",
                "Prótesis dental",
                "Otras"
            ].index(producto["tipo"]))

        col1, col2 = st.columns(2)
        with col1:
            material = st.text_input("Material *", value=producto["material"])
        with col2:
            precio = st.number_input("Precio (ARS) *", min_value=0.0, step=100.0, format="%.2f", value=float(producto["precio"]))

        col1, col2 = st.columns(2)
        with col1:
            peso_importado = st.number_input("Peso (kg)", min_value=0.0, step=0.1, format="%.2f", value=float(producto["peso_importado"] or 0))
        with col2:
            tiempo_entrega = st.number_input("Tiempo de entrega (días) *", min_value=1, max_value=365, value=int(producto["tiempo_entrega"] or 30))

        col1, col2 = st.columns(2)
        with col1:
            stock = st.number_input("Stock disponible", min_value=0, value=int(producto["stock"] or 0))
        with col2:
            imagen = st.text_input("URL de imagen", value=producto["imagen"] or "")

        descripcion = st.text_area("Descripción *", height=120, value=producto["descripcion"])

        st.markdown("### 🏥 Coberturas Disponibles")
        coberturas_seleccionadas = []

        if not coberturas_df.empty:
            cols = st.columns(2)
            for idx, (_, cobertura) in enumerate(coberturas_df.iterrows()):
                col = cols[idx % 2]
                with col:
                    checked = cobertura["id_cobertura"] in coberturas_actuales
                    if st.checkbox(f"{cobertura['nombre']} ({cobertura['porcentaje_cobertura']}%)", key=f"edit_cob_{cobertura['id_cobertura']}", value=checked):
                        coberturas_seleccionadas.append(cobertura['id_cobertura'])
                    if cobertura['descripcion']:
                        st.caption(cobertura['descripcion'])
        else:
            st.warning("⚠️ No hay coberturas disponibles.")

        submitted = st.form_submit_button("💾 Guardar cambios", type="primary")

    if submitted:
        try:
            nombre_sql = nombre.strip().replace("'", "''")
            tipo_sql = tipo.replace("'", "''")
            material_sql = material.strip().replace("'", "''")
            descripcion_sql = descripcion.strip().replace("'", "''")
            imagen_sql = f"'{imagen.strip()}'" if imagen.strip() else "NULL"
            peso_sql = peso_importado if peso_importado > 0 else "NULL"

            update_query = f"""
                UPDATE producto SET
                    nombre = '{nombre_sql}',
                    tipo = '{tipo_sql}',
                    material = '{material_sql}',
                    precio = {precio},
                    peso_importado = {peso_sql},
                    tiempo_entrega = {tiempo_entrega},
                    imagen = {imagen_sql},
                    descripcion = '{descripcion_sql}',
                    stock = {stock}
                WHERE id_producto = {id_producto};
            """
            execute_query(update_query, is_select=False)

            execute_query(f"DELETE FROM producto_cobertura WHERE id_producto = {id_producto}", is_select=False)
            for id_cob in coberturas_seleccionadas:
                insert_cob = f"INSERT INTO producto_cobertura (id_producto, id_cobertura) VALUES ({id_producto}, {id_cob});"
                execute_query(insert_cob, is_select=False)

            st.success("✅ Producto actualizado correctamente.")
            st.balloons()

            with st.expander("📄 Vista previa del producto editado", expanded=True):
                st.write(f"**Nombre:** {nombre}")
                st.write(f"**Tipo:** {tipo}")
                st.write(f"**Material:** {material}")
                st.write(f"**Precio:** ${precio:,.2f}")
                if peso_importado > 0:
                    st.write(f"**Peso:** {peso_importado} kg")
                st.write(f"**Tiempo de entrega:** {tiempo_entrega} días")
                if imagen.strip():
                    st.image(imagen, width=200)
                st.write(f"**Descripción:** {descripcion}")
                st.write(f"**Coberturas seleccionadas:** {len(coberturas_seleccionadas)}")

            st.markdown("---")
            if st.button("🏠 Volver al menú de empresa", use_container_width=True):
                st.session_state["vista"] = "vista_empresa"
                st.rerun()

        except Exception as e:
            st.error("❌ Error inesperado:")
            st.code(str(e))
