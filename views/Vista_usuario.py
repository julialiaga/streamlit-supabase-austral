import streamlit as st
import pandas as pd
from utils.db import execute_query
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles


def mostrar():
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("usuario")

    # Botón de volver
    if st.button("← Volver", key="volver_inicio", help="Cerrar sesión y volver al inicio"):
        # Limpiar session state de empresa
        if "empresa" in st.session_state:
            del st.session_state["empresa"]
        st.session_state["vista"] = "inicio"
        st.rerun()

    usuario = st.session_state.get("usuario", {})
    nombre_usuario = usuario.get("nombre", "Usuario")

    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #7BA7D1 0%, #5A8BC2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        '>
            <div style='font-size: 2rem; font-weight: bold;'>¡Hola, {nombre_usuario}!</div>
            <div style='font-size: 1.1rem;'>Explorá y consultá sobre las prótesis disponibles</div>
        </div>
    """, unsafe_allow_html=True)

    # Navegación mejorada
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📧 Ver mis consultas", key="ver_consultas_usuario", use_container_width=True):
            st.session_state["vista"] = "consultas_usuario"
            st.rerun()
    
    with col2:
        if st.button("🔄 Actualizar productos", key="refresh_productos", use_container_width=True):
            st.rerun()

    st.markdown("---")
    st.markdown("<h2 style='text-align:center;'>Explorar Prótesis Disponibles</h2>", unsafe_allow_html=True)

    # Cargar datos
    productos_df = execute_query("SELECT * FROM vista_productos_completa")
    coberturas_df = execute_query("SELECT * FROM coberturas ORDER BY nombre")

    if productos_df.empty:
        st.warning("No hay productos disponibles en este momento.")
        return

    # Sidebar de filtros mejorado
    with st.sidebar:
        st.header("🔍 Filtros de búsqueda")
        st.markdown("---")

        # Búsqueda por texto
        buscar = st.text_input("Buscar productos", placeholder="Ej: prótesis de pierna", help="Busca por nombre del producto")
        
        # Filtros categóricos
        tipos = ["Todos"] + sorted(productos_df["tipo"].dropna().unique().tolist())
        materiales = ["Todos"] + sorted(productos_df["material"].dropna().unique().tolist())
        empresas = ["Todas"] + sorted(productos_df["nombre_empresa"].dropna().unique().tolist())

        tipo_select = st.selectbox("Tipo de prótesis", options=tipos)
        material_select = st.selectbox("Material", options=materiales)
        empresa_select = st.selectbox("Empresa", options=empresas)
        
        # Filtro de precio
        precio_min, precio_max = st.slider(
            "Rango de precio (ARS)", 
            min_value=0, 
            max_value=int(productos_df["precio"].max()), 
            value=(0, int(productos_df["precio"].max())),
            step=1000,
            format="$%d"
        )

        # Filtro por stock
        solo_con_stock = st.checkbox("Solo productos con stock disponible", value=True)
        
        # Filtro por cobertura (implementado)
        if not coberturas_df.empty:
            cobertura_nombres = ["Todas"] + coberturas_df["nombre"].tolist()
            cobertura_select = st.selectbox("Cobertura médica", options=cobertura_nombres)
        else:
            cobertura_select = "Todas"

        # Botón de limpiar filtros
        if st.button("🗑 Limpiar filtros", use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.caption(f"Mostrando {len(productos_df)} productos")

    # Aplicar filtros
    productos_filtrados = productos_df.copy()

    # Filtro de búsqueda
    if buscar:
        productos_filtrados = productos_filtrados[
            productos_filtrados["nombre_producto"].str.contains(buscar, case=False, na=False) |
            productos_filtrados["descripcion"].str.contains(buscar, case=False, na=False)
        ]

    # Filtros categóricos
    if tipo_select != "Todos":
        productos_filtrados = productos_filtrados[productos_filtrados["tipo"] == tipo_select]

    if material_select != "Todos":
        productos_filtrados = productos_filtrados[productos_filtrados["material"] == material_select]
    
    if empresa_select != "Todas":
        productos_filtrados = productos_filtrados[productos_filtrados["nombre_empresa"] == empresa_select]

    # Filtro de precio
    productos_filtrados = productos_filtrados[
        (productos_filtrados["precio"] >= precio_min) & 
        (productos_filtrados["precio"] <= precio_max)
    ]

    # Filtro de stock
    if solo_con_stock:
        productos_filtrados = productos_filtrados[productos_filtrados["stock"] > 0]

    # Implementar filtro por cobertura (si tienes una tabla de relación producto-cobertura)
    if cobertura_select != "Todas":
        # Aquí necesitarías implementar la lógica según tu estructura de BD
        # Por ejemplo, si tienes una tabla producto_cobertura:
        # cobertura_id_query = f"SELECT id FROM coberturas WHERE nombre = '{cobertura_select}'"
        # cobertura_id = execute_query(cobertura_id_query).iloc[0]['id'] if not execute_query(cobertura_id_query).empty else None
        # if cobertura_id:
        #     productos_con_cobertura = execute_query(f"SELECT id_producto FROM producto_cobertura WHERE id_cobertura = {cobertura_id}")
        #     productos_filtrados = productos_filtrados[productos_filtrados["id_producto"].isin(productos_con_cobertura["id_producto"])]
        pass

    productos_filtrados = productos_filtrados.reset_index(drop=True)

    # Mostrar cantidad de resultados
    st.info(f"Se encontraron {len(productos_filtrados)} productos que coinciden con tus filtros.")

    if productos_filtrados.empty:
        st.warning("No se encontraron productos con los filtros aplicados. Intenta modificar los criterios de búsqueda.")
        return

    # Sistema de comparación mejorado
    if "productos_comparacion" not in st.session_state:
        st.session_state["productos_comparacion"] = []

    # Mostrar productos
    productos_seleccionados = []

    for i in range(0, len(productos_filtrados), 2):
        cols = st.columns(2)

        for j in range(2):
            if i + j >= len(productos_filtrados):
                break
            producto = productos_filtrados.iloc[i + j]

            with cols[j]:
                st.markdown(f"""
                    <div style='
                        border: 1px solid #e0e0e0; 
                        border-radius: 12px; 
                        padding: 1.5rem; 
                        margin-bottom: 1rem; 
                        background-color: #ffffff; 
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        transition: transform 0.2s;
                    '>
                        <h4 style='margin-bottom: 0.8rem; color: #2c3e50;'>{producto['nombre_producto']}</h4>
                        <div style='margin-bottom: 1rem;'>
                            <span style='background-color: #f8f9fa; padding: 0.3rem 0.6rem; border-radius: 15px; font-size: 0.85rem; margin-right: 0.5rem;'>
                                {producto['tipo']}
                            </span>
                            <span style='background-color: #e9ecef; padding: 0.3rem 0.6rem; border-radius: 15px; font-size: 0.85rem;'>
                                {producto['material']}
                            </span>
                        </div>
                        <p style='margin: 0.5rem 0; font-size: 1.2rem; font-weight: bold; color: #27ae60;'>
                             ${producto['precio']:,.2f}
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                # Expander para detalles del producto
                with st.expander(f"*Ver detalles del producto*", expanded=False):
                    # Descripción primero
                    if producto.get("descripcion") and not pd.isna(producto["descripcion"]):
                        st.markdown("*Descripción:*")
                        st.write(producto["descripcion"])
                        
                    
                    # Información técnica y especificaciones
                    st.markdown("*Información del producto:*")
                    st.write(f"*Tiempo de entrega:* {producto['tiempo_entrega']} días")
                    st.write(f"*Stock disponible:* {producto['stock']} unidades")
                    st.write(f"*Empresa:* {producto['nombre_empresa']}")
                    if not pd.isna(producto.get('peso_importado')):
                        st.write(f"*Peso:* {producto['peso_importado']} kg")
                    st.write(f"*Tipo:* {producto['tipo']}")
                    st.write(f"*Material:* {producto['material']}")
                    
                    # Información adicional si existe
                    if any(not pd.isna(producto.get(field)) for field in ['dimension', 'color', 'garantia']):
                        st.markdown("---")
                        st.markdown("ℹInformación adicional:")
                        if not pd.isna(producto.get('dimension')):
                            st.write(f"*Dimensiones:* {producto['dimension']}")
                        if not pd.isna(producto.get('color')):
                            st.write(f"*Color:* {producto['color']}")
                        if not pd.isna(producto.get('garantia')):
                            st.write(f"*Garantía:* {producto['garantia']}")
                
                # Comparar producto
                comparar_checked = st.checkbox("Comparar producto", key=f"compare_{producto['id_producto']}")
                if comparar_checked:
                    if producto['id_producto'] not in [p['id_producto'] for p in st.session_state["productos_comparacion"]]:
                        st.session_state["productos_comparacion"].append(producto.to_dict())
                else:
                    st.session_state["productos_comparacion"] = [
                        p for p in st.session_state["productos_comparacion"] 
                        if p['id_producto'] != producto['id_producto']
                    ]

                # Fila 2: Consultar (botón principal)
                if producto['stock'] > 0:
                    if st.button("Enviar consulta a la empresa", key=f"consultar_{producto['id_producto']}", use_container_width=True, type="primary"):
                        st.session_state[f"show_consulta_{producto['id_producto']}"] = not st.session_state.get(f"show_consulta_{producto['id_producto']}", False)
                else:
                    st.button("❌ Sin stock disponible", key=f"no_stock_{producto['id_producto']}", disabled=True, use_container_width=True)

                # Formulario de consulta simplificado
                if st.session_state.get(f"show_consulta_{producto['id_producto']}", False):
                    st.markdown(f"""
                        <div style='
                            background-color: #e8f4f8; 
                            border-left: 4px solid #5A8BC2; 
                            padding: 1rem; 
                            margin: 1rem 0; 
                            border-radius: 8px;
                        '>
                            <p><strong>Consulta para: {producto['nombre_producto']} </strong></p>
                            <p>Tu consulta será enviada a: <strong><em> {producto['nombre_empresa']} </em></strong></p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    #st.markdown(f"*Consulta para: {producto['nombre_producto']}*")
                    #st.write(f"Tu consulta será enviada a: *{producto['nombre_empresa']}*")
                    
                    with st.form(f"form_consulta_{producto['id_producto']}"):
                        mensaje = st.text_area(
                            "Escribe tu consulta:", 
                            height=120,
                            key=f"msg_{producto['id_producto']}",
                            placeholder="Ejemplo: Me interesa este producto, ¿podrían brindarme más información sobre disponibilidad y precio?",
                            help="Describe tu consulta de manera clara y específica"
                        )
                        
                        # Información de contacto opcional
                        incluir_contacto = st.checkbox("Incluir mi información de contacto en el mensaje", key=f"contacto_{producto['id_producto']}")
                        
                        col_form1, col_form2 = st.columns(2)
                        with col_form1:
                            enviar = st.form_submit_button("Enviar consulta", use_container_width=True, type="primary")
                        with col_form2:
                            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)

                        if cancelar:
                            st.session_state[f"show_consulta_{producto['id_producto']}"] = False
                            st.rerun()

                        if enviar:
                            if not mensaje.strip():
                                st.error("Por favor, escribe un mensaje antes de enviar.")
                            elif len(mensaje.strip()) < 10:
                                st.error("El mensaje debe tener al menos 10 caracteres.")
                            else:
                                usuario = st.session_state.get("usuario", {})
                                if not usuario:
                                    st.error("Error: No se pudo identificar tu usuario. Por favor, inicia sesión nuevamente.")
                                else:
                                    # Preparar mensaje final
                                    mensaje_final = mensaje.strip()
                                    if incluir_contacto:
                                        mensaje_final += f"\n\n--- Información de contacto ---\nUsuario: {usuario.get('nombre', 'No especificado')}"
                                        if usuario.get('email'):
                                            mensaje_final += f"\nEmail: {usuario['email']}"
                                    
                                    # Escapar comillas para SQL
                                    mensaje_sql = mensaje_final.replace("'", "''")
                                    
                                    id_usuario = usuario.get("id_usuario") or usuario.get("ID_usuario")
                                    id_empresa = producto["id_empresa"]
                                    id_producto = producto["id_producto"]

                                    query_insert = f"""
                                        INSERT INTO consulta (id_usuario, id_empresa, id_producto, mensaje, fecha_consulta)
                                        VALUES ({id_usuario}, {id_empresa}, {id_producto}, '{mensaje_sql}', NOW());
                                    """

                                    try:
                                        success = execute_query(query_insert, is_select=False)
                                        if success:
                                            st.success("✅ ¡Consulta enviada exitosamente! La empresa se pondrá en contacto contigo pronto.")
                                            st.session_state[f"show_consulta_{producto['id_producto']}"] = False
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al enviar la consulta. Por favor, intenta nuevamente.")
                                    except Exception as e:
                                        st.error(f"❌ Error inesperado: {str(e)}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)

    # Sistema de comparación mejorado
    if st.session_state["productos_comparacion"]:
        st.markdown("---")
        st.markdown("### ⚖ Comparación de productos seleccionados")
        
        col_comp1, col_comp2 = st.columns([3, 1])
        with col_comp1:
            st.info(f"Has seleccionado {len(st.session_state['productos_comparacion'])} productos para comparar")
        with col_comp2:
            if st.button("🗑 Limpiar comparación"):
                st.session_state["productos_comparacion"] = []
                st.rerun()

        comparacion_df = pd.DataFrame(st.session_state["productos_comparacion"])[[
            "nombre_producto", "tipo", "material", "precio", "peso_importado", 
            "tiempo_entrega", "stock", "nombre_empresa"
        ]]

        # Renombrar columnas para mejor presentación
        comparacion_df = comparacion_df.rename(columns={
            "nombre_producto": "Producto",
            "tipo": "Tipo",
            "material": "Material",
            "precio": "Precio (ARS)",
            "peso_importado": "Peso (kg)",
            "tiempo_entrega": "Entrega (días)",
            "stock": "Stock",
            "nombre_empresa": "Empresa"
        })

        # Formatear la tabla
        st.dataframe(
            comparacion_df.set_index("Producto"),
            use_container_width=True,
            column_config={
                "Precio (ARS)": st.column_config.NumberColumn(
                    "Precio (ARS)",
                    format="$%.2f"
                ),
                "Peso (kg)": st.column_config.NumberColumn(
                    "Peso (kg)",
                    format="%.2f kg"
                ),
                "Entrega (días)": st.column_config.NumberColumn(
                    "Entrega (días)",
                    format="%d días"
                )
            }
        )

    #add_footer()