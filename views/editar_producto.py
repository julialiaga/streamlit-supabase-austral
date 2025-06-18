import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query

@st.cache_data(ttl=600)  # Cache por 10 minutos
def obtener_coberturas():
    """Obtiene las coberturas disponibles con cache"""
    return execute_query("SELECT * FROM coberturas ORDER BY nombre")

@st.cache_data(ttl=300)  # Cache por 5 minutos
def obtener_coberturas_producto(id_producto):
    """Obtiene las coberturas actuales del producto con cache"""
    query = "SELECT id_cobertura FROM producto_cobertura WHERE id_producto = %s"
    result = execute_query(query, (id_producto,))
    return result["id_cobertura"].tolist() if not result.empty else []

def validar_campos_obligatorios(nombre, tipo, material, precio, tiempo_entrega, descripcion):
    """Valida los campos obligatorios del formulario"""
    errores = []
    
    if not nombre.strip():
        errores.append("El nombre del producto es obligatorio")
    if not material.strip():
        errores.append("El material es obligatorio")
    if precio <= 0:
        errores.append("El precio debe ser mayor a 0")
    if tiempo_entrega <= 0:
        errores.append("El tiempo de entrega debe ser mayor a 0")
    if not descripcion.strip():
        errores.append("La descripción es obligatoria")
    
    return errores

def sanitizar_entrada(texto):
    """Sanitiza las entradas de texto para prevenir inyección SQL"""
    if texto is None:
        return ""
    return str(texto).strip().replace("'", "''")

def actualizar_producto(id_producto, datos_producto, coberturas_seleccionadas):
    """Actualiza el producto y sus coberturas de manera transaccional"""
    try:
        # Preparar datos sanitizados
        nombre_sql = sanitizar_entrada(datos_producto['nombre'])
        tipo_sql = sanitizar_entrada(datos_producto['tipo'])
        material_sql = sanitizar_entrada(datos_producto['material'])
        descripcion_sql = sanitizar_entrada(datos_producto['descripcion'])
        imagen_sql = sanitizar_entrada(datos_producto['imagen']) if datos_producto['imagen'] else None
        peso_sql = datos_producto['peso'] if datos_producto['peso'] > 0 else None

        # Query parametrizada para mayor seguridad
        update_query = """
            UPDATE producto SET
                nombre = %s,
                tipo = %s,
                material = %s,
                precio = %s,
                peso_importado = %s,
                tiempo_entrega = %s,
                imagen = %s,
                descripcion = %s,
                stock = %s
            WHERE id_producto = %s
        """
        
        parametros = (
            nombre_sql, tipo_sql, material_sql, datos_producto['precio'],
            peso_sql, datos_producto['tiempo_entrega'], imagen_sql,
            descripcion_sql, datos_producto['stock'], id_producto
        )
        
        execute_query(update_query, parametros, is_select=False)

        # Actualizar coberturas
        execute_query("DELETE FROM producto_cobertura WHERE id_producto = %s", 
                     (id_producto,), is_select=False)
        
        for id_cob in coberturas_seleccionadas:
            execute_query(
                "INSERT INTO producto_cobertura (id_producto, id_cobertura) VALUES (%s, %s)",
                (id_producto, id_cob), is_select=False
            )
        
        return True, None
    except Exception as e:
        return False, str(e)

def renderizar_vista_previa(datos_producto, num_coberturas):
    """Renderiza la vista previa del producto de manera optimizada"""
    vista_html = f"""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
        <h4>📄 Vista previa del producto editado</h4>
        <p><strong>Nombre:</strong> {datos_producto['nombre']}</p>
        <p><strong>Tipo:</strong> {datos_producto['tipo']}</p>
        <p><strong>Material:</strong> {datos_producto['material']}</p>
        <p><strong>Precio:</strong> ${datos_producto['precio']:,.2f}</p>
        {f"<p><strong>Peso:</strong> {datos_producto['peso']} kg</p>" if datos_producto['peso'] > 0 else ""}
        <p><strong>Tiempo de entrega:</strong> {datos_producto['tiempo_entrega']} días</p>
        <p><strong>Descripción:</strong> {datos_producto['descripcion']}</p>
        <p><strong>Coberturas seleccionadas:</strong> {num_coberturas}</p>
    </div>
    """
    
    st.markdown(vista_html, unsafe_allow_html=True)
    
    if datos_producto['imagen']:
        st.image(datos_producto['imagen'], width=200, caption="Imagen del producto")

def mostrar():
    # Verificación temprana del producto
    producto = st.session_state.get("producto_a_editar", {})
    if not producto:
        st.error("No se encontró el producto a editar.")
        return

    # Configuración de estilos solo una vez por sesión
    if "edit_styles_loaded" not in st.session_state:
        set_global_styles()
        add_page_specific_styles("empresa")
        st.session_state["edit_styles_loaded"] = True
    
    add_logo_and_header()

    st.markdown('<h2 class="registro-title">Editar Producto</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    id_producto = producto.get("id_producto")

    # Navegación
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Volver"):
            st.session_state["vista"] = "vista_empresa"
            st.rerun()

    st.markdown("---")

    # Carga de datos con spinner
    with st.spinner('Cargando información del producto...'):
        try:
            coberturas_df = obtener_coberturas()
            coberturas_actuales = obtener_coberturas_producto(id_producto)
        except Exception as e:
            st.error(f"Error al cargar los datos: {str(e)}")
            return

    # Tipos de prótesis como constante para evitar repetición
    TIPOS_PROTESIS = [
        "Prótesis de miembro superior",
        "Prótesis de miembro inferior", 
        "Prótesis de mano",
        "Prótesis de pie",
        "Prótesis facial",
        "Prótesis dental",
        "Otras"
    ]

    with st.form("form_editar_producto"):
        st.markdown("### Información del Producto")

        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del producto *", value=producto["nombre_producto"])
        with col2:
            tipo_index = TIPOS_PROTESIS.index(producto["tipo"]) if producto["tipo"] in TIPOS_PROTESIS else 0
            tipo = st.selectbox("Tipo de prótesis *", TIPOS_PROTESIS, index=tipo_index)

        col1, col2 = st.columns(2)
        with col1:
            material = st.text_input("Material *", value=producto["material"])
        with col2:
            precio = st.number_input("Precio (ARS) *", min_value=0.0, step=100.0, 
                                   format="%.2f", value=float(producto["precio"]))

        col1, col2 = st.columns(2)
        with col1:
            peso_importado = st.number_input("Peso (kg)", min_value=0.0, step=0.1, 
                                           format="%.2f", value=float(producto["peso_importado"] or 0))
        with col2:
            tiempo_entrega = st.number_input("Tiempo de entrega (días) *", min_value=1, max_value=365, 
                                           value=int(producto["tiempo_entrega"] or 30))

        col1, col2 = st.columns(2)
        with col1:
            stock = st.number_input("Stock disponible", min_value=0, value=int(producto["stock"] or 0))
        with col2:
            imagen = st.text_input("URL de imagen", value=producto["imagen"] or "")

        descripcion = st.text_area("Descripción *", height=120, value=producto["descripcion"])

        st.markdown("### 🏥 Coberturas Disponibles")
        coberturas_seleccionadas = []

        if not coberturas_df.empty:
            # Renderizar coberturas en batch para mejor performance
            cols = st.columns(2)
            for idx, (_, cobertura) in enumerate(coberturas_df.iterrows()):
                col = cols[idx % 2]
                with col:
                    checked = cobertura["id_cobertura"] in coberturas_actuales
                    key = f"edit_cob_{cobertura['id_cobertura']}"
                    
                    if st.checkbox(f"{cobertura['nombre']} ({cobertura['porcentaje_cobertura']}%)", 
                                 key=key, value=checked):
                        coberturas_seleccionadas.append(cobertura['id_cobertura'])
                    
                    if cobertura['descripcion']:
                        st.caption(cobertura['descripcion'])
        else:
            st.warning("⚠️ No hay coberturas disponibles.")

        submitted = st.form_submit_button("💾 Guardar cambios", type="primary")

    if submitted:
        # Validación de campos
        errores = validar_campos_obligatorios(nombre, tipo, material, precio, tiempo_entrega, descripcion)
        
        if errores:
            for error in errores:
                st.error(f"❌ {error}")
            return

        # Preparar datos
        datos_producto = {
            'nombre': nombre,
            'tipo': tipo,
            'material': material,
            'precio': precio,
            'peso': peso_importado,
            'tiempo_entrega': tiempo_entrega,
            'imagen': imagen.strip() if imagen.strip() else None,
            'descripcion': descripcion,
            'stock': stock
        }

        # Actualizar producto con spinner
        with st.spinner('Actualizando producto...'):
            exito, error = actualizar_producto(id_producto, datos_producto, coberturas_seleccionadas)

        if exito:
            # Limpiar cache después de la actualización
            obtener_coberturas_producto.clear()
            
            st.success("✅ Producto actualizado correctamente.")
            st.balloons()

            # Vista previa optimizada
            renderizar_vista_previa(datos_producto, len(coberturas_seleccionadas))

            st.markdown("---")
            if st.button("🏠 Volver al menú de empresa", use_container_width=True):
                st.session_state["vista"] = "vista_empresa"
                st.rerun()
        else:
            st.error(f"❌ Error al actualizar el producto: {error}")