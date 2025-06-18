import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query

# CACHE PRINCIPAL - Evita consultas repetitivas
@st.cache_data(ttl=600)
def cargar_coberturas():
    return execute_query("SELECT * FROM coberturas ORDER BY nombre")

def validar_producto_form(datos):
    errores = []
    if not datos['nombre'].strip():
        errores.append("El nombre es obligatorio.")
    if not datos['tipo']:
        errores.append("Debes seleccionar un tipo de prótesis.")
    if not datos['material'].strip():
        errores.append("El material es obligatorio.")
    if datos['precio'] <= 0:
        errores.append("El precio debe ser mayor a cero.")
    if datos['tiempo_entrega'] <= 0:
        errores.append("El tiempo de entrega debe ser mayor a cero.")
    if not datos['descripcion'].strip():
        errores.append("La descripción es obligatoria.")
    return errores

def procesar_insercion_producto(datos, id_empresa, coberturas_seleccionadas):
    try:
        nombre_sql = datos['nombre'].strip().replace("'", "''")
        tipo_sql = datos['tipo'].replace("'", "''")
        material_sql = datos['material'].strip().replace("'", "''")
        descripcion_sql = datos['descripcion'].strip().replace("'", "''")
        imagen_sql = f"'{datos['imagen'].strip()}'" if datos['imagen'].strip() else "NULL"
        peso_sql = datos['peso_importado'] if datos['peso_importado'] > 0 else "NULL"

        insert_query = f"""
            INSERT INTO producto (
                id_empresa, nombre, tipo, material, precio,
                peso_importado, tiempo_entrega, imagen, descripcion, stock
            ) VALUES (
                {id_empresa}, '{nombre_sql}', '{tipo_sql}', '{material_sql}', {datos['precio']},
                {peso_sql}, {datos['tiempo_entrega']}, {imagen_sql}, '{descripcion_sql}', {datos['stock']}
            );
        """

        with st.spinner("Guardando producto..."):
            success = execute_query(insert_query, is_select=False)

        if success:
            id_query = f"""
                SELECT id_producto FROM producto
                WHERE id_empresa = {id_empresa}
                ORDER BY id_producto DESC LIMIT 1;
            """
            result = execute_query(id_query)
            id_producto = result.iloc[0]["id_producto"] if not result.empty else None

            if coberturas_seleccionadas and id_producto:
                with st.spinner("Registrando coberturas..."):
                    for id_cob in coberturas_seleccionadas:
                        insert_cob = f"""
                            INSERT INTO producto_cobertura (id_producto, id_cobertura)
                            VALUES ({id_producto}, {id_cob});
                        """
                        execute_query(insert_cob, is_select=False)

            return True, datos
        else:
            return False, None

    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        return False, None

def mostrar_resumen_producto(datos):
    with st.expander("📄 Resumen del producto creado", expanded=True):
        st.write(f"**Nombre:** {datos['nombre']}")
        st.write(f"**Tipo:** {datos['tipo']}")
        st.write(f"**Material:** {datos['material']}")
        st.write(f"**Precio:** ${datos['precio']:,.2f}")
        if datos['peso_importado'] > 0:
            st.write(f"**Peso:** {datos['peso_importado']} kg")
        st.write(f"**Tiempo de entrega:** {datos['tiempo_entrega']} días")
        if datos['imagen'].strip():
            st.image(datos['imagen'], width=200)
        st.write(f"**Descripción:** {datos['descripcion']}")

def mostrar_coberturas_disponibles(coberturas_df):
    st.markdown("### 🏥 Coberturas Disponibles")
    coberturas_seleccionadas = []

    if not coberturas_df.empty:
        if "coberturas_seleccionadas" not in st.session_state:
            st.session_state.coberturas_seleccionadas = []

        cols = st.columns(2)
        for idx, (_, cobertura) in enumerate(coberturas_df.iterrows()):
            col = cols[idx % 2]
            with col:
                checked = st.checkbox(
                    f"{cobertura['nombre']} ({cobertura['porcentaje_cobertura']}%)",
                    key=f"cob_{cobertura['id_cobertura']}",
                    value=cobertura['id_cobertura'] in st.session_state.coberturas_seleccionadas
                )

                if checked and cobertura['id_cobertura'] not in st.session_state.coberturas_seleccionadas:
                    st.session_state.coberturas_seleccionadas.append(cobertura['id_cobertura'])
                elif not checked and cobertura['id_cobertura'] in st.session_state.coberturas_seleccionadas:
                    st.session_state.coberturas_seleccionadas.remove(cobertura['id_cobertura'])

                if checked:
                    coberturas_seleccionadas.append(cobertura['id_cobertura'])

                if cobertura['descripcion']:
                    st.caption(cobertura['descripcion'])
    else:
        st.warning("⚠️ No hay coberturas disponibles.")

    return coberturas_seleccionadas

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

    st.markdown("---")

    with st.spinner("Cargando coberturas disponibles..."):
        coberturas_df = cargar_coberturas()

    with st.form("form_cargar_producto", clear_on_submit=False):
        st.markdown("### Información del Producto")

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

        col1, col2 = st.columns(2)
        with col1:
            material = st.text_input("Material *", placeholder="Ej: Fibra de carbono, Titanio, Silicona")
        with col2:
            precio = st.number_input("Precio (ARS) *", min_value=0.0, step=100.0, format="%.2f")

        col1, col2 = st.columns(2)
        with col1:
            peso_importado = st.number_input("Peso (kg)", min_value=0.0, step=0.1, format="%.2f")
        with col2:
            tiempo_entrega = st.number_input("Tiempo de entrega (días) *", min_value=1, max_value=365, value=30)

        col1, col2 = st.columns(2)
        with col1:
            stock = st.number_input("Stock disponible", min_value=0, value=0)
        with col2:
            imagen = st.text_input("URL de imagen", placeholder="https://ejemplo.com/imagen.jpg")

        descripcion = st.text_area("Descripción *", height=120, placeholder="Describe características y especificaciones...")

        coberturas_seleccionadas = mostrar_coberturas_disponibles(coberturas_df)

        submitted = st.form_submit_button("Guardar Producto", type="primary")

    if submitted:
        datos_producto = {
            'nombre': nombre,
            'tipo': tipo,
            'material': material,
            'precio': precio,
            'peso_importado': peso_importado,
            'tiempo_entrega': tiempo_entrega,
            'stock': stock,
            'imagen': imagen,
            'descripcion': descripcion
        }

        errores = validar_producto_form(datos_producto)

        if errores:
            st.warning("⚠️ Corrige los siguientes errores:")
            for e in errores:
                st.write(f"• {e}")
        else:
            exito, datos_guardados = procesar_insercion_producto(
                datos_producto,
                id_empresa,
                coberturas_seleccionadas
            )

            if exito:
                try:
                    from views import productos_empresa
                    if hasattr(productos_empresa, "obtener_productos_empresa"):
                        productos_empresa.obtener_productos_empresa.clear()
                    if hasattr(productos_empresa, "obtener_coberturas_producto"):
                        productos_empresa.obtener_coberturas_producto.clear()
                except Exception:
                    pass

                st.session_state["mensaje_exito"] = "✅ Producto cargado correctamente."
                st.session_state["vista"] = "vista_empresa"
                st.rerun()
            else:
                st.error("❌ Ocurrió un error al guardar el producto.")

    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("¿No encuentras la cobertura que buscas?")
    with col2:
        if st.button("🔄 Actualizar coberturas", help="Recargar lista de coberturas disponibles"):
            cargar_coberturas.clear()
            st.rerun()
