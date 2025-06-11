import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query

def mostrar():
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("empresa")

    st.markdown('<h2 class="registro-title">Cargar Nuevo Producto</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")

    if not id_empresa:
        st.error("No se encontró la sesión de empresa.")
        return

    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Volver"):
            st.session_state["vista"] = "vista_empresa"
            st.rerun()

    st.markdown("---")

    with st.form("form_cargar_producto", clear_on_submit=False):
        st.markdown("### Información del Producto")

        # Fila 1: Nombre y Tipo
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del producto *", placeholder="Ej: Prótesis transtibial deportiva")
        with col2:
            tipo = st.selectbox("Tipo de prótesis *", [
                "Prótesis de miembro superior",
                "Prótesis de miembro inferior",
                "Prótesis de mano",
                "Prótesis de pie",
                "Prótesis facial",
                "Prótesis dental",
                "Otras"
            ])

        # Fila 2: Material y Precio
        col1, col2 = st.columns(2)
        with col1:
            material = st.text_input("Material *", placeholder="Ej: Fibra de carbono, Titanio, Silicona")
        with col2:
            precio = st.number_input("Precio (ARS) *", min_value=0.0, step=100.0, format="%.2f")

        # Fila 3: Peso y Tiempo de entrega
        col1, col2 = st.columns(2)
        with col1:
            peso_importado = st.number_input("Peso (kg)", min_value=0.0, step=0.1, format="%.2f")
        with col2:
            tiempo_entrega = st.number_input("Tiempo de entrega (días) *", min_value=1, max_value=365, value=30)

        # Fila 4: Stock e Imagen
        col1, col2 = st.columns(2)
        with col1:
            stock = st.number_input("Stock disponible", min_value=0, value=0)
        with col2:
            imagen = st.text_input("URL de imagen", placeholder="https://ejemplo.com/imagen.jpg")

        descripcion = st.text_area("Descripción *", height=120, placeholder="Describe características y especificaciones...")

        # Coberturas
        st.markdown("### 🏥 Coberturas Disponibles")
        coberturas_df = execute_query("SELECT * FROM coberturas ORDER BY nombre")
        coberturas_seleccionadas = []

        if not coberturas_df.empty:
            cols = st.columns(2)
            for idx, (_, cobertura) in enumerate(coberturas_df.iterrows()):
                col = cols[idx % 2]
                with col:
                    if st.checkbox(f"{cobertura['nombre']} ({cobertura['porcentaje_cobertura']}%)", key=f"cob_{cobertura['id_cobertura']}"):
                        coberturas_seleccionadas.append(cobertura['id_cobertura'])
                    if cobertura['descripcion']:
                        st.caption(cobertura['descripcion'])
        else:
            st.warning("⚠️ No hay coberturas disponibles.")

        submitted = st.form_submit_button("Guardar Producto", type="primary")

    if submitted:
        errores = []
        if not nombre.strip():
            errores.append("El nombre es obligatorio.")
        if not tipo:
            errores.append("Debes seleccionar un tipo de prótesis.")
        if not material.strip():
            errores.append("El material es obligatorio.")
        if precio <= 0:
            errores.append("El precio debe ser mayor a cero.")
        if tiempo_entrega <= 0:
            errores.append("El tiempo de entrega debe ser mayor a cero.")
        if not descripcion.strip():
            errores.append("La descripción es obligatoria.")

        if errores:
            st.warning("⚠️ Corrige los siguientes errores:")
            for e in errores:
                st.write(f"• {e}")
        else:
            try:
                nombre_sql = nombre.strip().replace("'", "''")
                tipo_sql = tipo.replace("'", "''")
                material_sql = material.strip().replace("'", "''")
                descripcion_sql = descripcion.strip().replace("'", "''")
                imagen_sql = f"'{imagen.strip()}'" if imagen.strip() else "NULL"
                peso_sql = peso_importado if peso_importado > 0 else "NULL"

                insert_query = f"""
                    INSERT INTO producto (
                        id_empresa, nombre, tipo, material, precio,
                        peso_importado, tiempo_entrega, imagen, descripcion, stock
                    ) VALUES (
                        {id_empresa}, '{nombre_sql}', '{tipo_sql}', '{material_sql}', {precio},
                        {peso_sql}, {tiempo_entrega}, {imagen_sql}, '{descripcion_sql}', {stock}
                    );
                """

                success = execute_query(insert_query, is_select=False)

                if success:
                    # Obtener el ID del nuevo producto
                    id_query = f"""
                        SELECT id_producto FROM producto
                        WHERE id_empresa = {id_empresa}
                        ORDER BY id_producto DESC LIMIT 1;
                    """
                    result = execute_query(id_query)
                    id_producto = result.iloc[0]["id_producto"] if not result.empty else None

                    # Registrar coberturas
                    for id_cob in coberturas_seleccionadas:
                        insert_cob = f"""
                            INSERT INTO producto_cobertura (id_producto, id_cobertura)
                            VALUES ({id_producto}, {id_cob});
                        """
                        execute_query(insert_cob, is_select=False)

                    st.success("✅ Producto cargado exitosamente.")
                    st.balloons()

                    with st.expander("📄 Resumen del producto creado", expanded=True):
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
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cargar otro producto", use_container_width=True):
                            st.session_state["vista"] = "Cargar_producto"
                            st.rerun()
                    with col2:
                        if st.button("🏠 Volver al menú de empresa", use_container_width=True):
                            st.session_state["vista"] = "vista_empresa"
                            st.rerun()
                else:
                    st.error("❌ Ocurrió un error al guardar el producto.")
            except Exception as e:
                st.error("❌ Error inesperado:")
                st.code(str(e))
