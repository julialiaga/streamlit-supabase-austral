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

    # Botón de ver consultas
    if st.button("Ver mis consultas", key="ver_consultas_usuario", use_container_width=True):
        st.session_state["vista"] = "consultas_usuario"
        st.rerun()


    st.markdown("---")

    st.markdown("<h2 style='text-align:center;'>Explorar Prótesis Disponibles</h2>", unsafe_allow_html=True)

    # Cargar datos
    productos_df = execute_query("SELECT * FROM vista_productos_completa")
    coberturas_df = execute_query("SELECT * FROM coberturas ORDER BY nombre")

    if productos_df.empty:
        st.warning("No hay productos disponibles en este momento.")
        return

    # Sidebar de filtros
    with st.sidebar:
        st.header("Filtros")

        buscar = st.text_input("🔍 Buscar productos...", placeholder="Ej: prótesis de pierna")
        tipos = productos_df["tipo"].dropna().unique().tolist()
        materiales = productos_df["material"].dropna().unique().tolist()

        tipo_select = st.multiselect("Tipo de prótesis", options=tipos)
        material_select = st.multiselect("Material", options=materiales)
        precio_min, precio_max = st.slider("Rango de precio", 0, int(productos_df["precio"].max()), (0, int(productos_df["precio"].max())))

        cobertura_nombres = coberturas_df["nombre"].tolist()
        cobertura_select = st.multiselect("Cobertura médica", options=cobertura_nombres)

        aplicar_filtros = st.button("Aplicar filtros")

    # Filtrar productos según criterios
    if buscar:
        productos_df = productos_df[productos_df["nombre_producto"].str.contains(buscar, case=False)]

    if tipo_select:
        productos_df = productos_df[productos_df["tipo"].isin(tipo_select)]

    if material_select:
        productos_df = productos_df[productos_df["material"].isin(material_select)]

    productos_df = productos_df[(productos_df["precio"] >= precio_min) & (productos_df["precio"] <= precio_max)]



    productos_df = productos_df.reset_index(drop=True)
    productos_seleccionados = []

    for i in range(0, len(productos_df), 2):
        cols = st.columns(2)

        for j in range(2):
            if i + j >= len(productos_df):
                break
            producto = productos_df.iloc[i + j]

            with cols[j]:
                with st.container():
                    st.markdown(f"""
                        <div style='border: 1px solid #e0e0e0; border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; background-color: #ffffff; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);'>
                            <h5 style='margin-bottom: 0.5rem;'>{producto['nombre_producto']}</h5>
                            <p><strong>Material:</strong> {producto['material']}</p>
                            <p><strong>Tipo:</strong> {producto['tipo']}</p>
                            <p><strong>Precio:</strong> ${producto['precio']:,.2f}</p>
                            <p><strong>Empresa:</strong> {producto['nombre_empresa']}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    with st.expander("📄 Ver más detalles"):
                        if producto.get("descripcion"):
                            st.write(producto["descripcion"])

                        st.write(f"Tiempo entrega: {producto['tiempo_entrega']} días")
                        if not pd.isna(producto['peso_importado']):
                            st.write(f"Peso: {producto['peso_importado']} kg")
                        st.write(f"Stock: {producto['stock']} unidades")
                    
                    if st.checkbox("Comparar", key=f"compare_{producto['id_producto']}"):
                        productos_seleccionados.append(producto)
                       
                        # Consulta
                        with st.form(f"form_consulta_{producto['id_producto']}"):
                            st.write("✉️ Enviar consulta a la empresa:")
                            mensaje = st.text_area("Mensaje", key=f"msg_{producto['id_producto']}")
                            enviar = st.form_submit_button("Enviar")

                            if enviar:
                                usuario = st.session_state.get("usuario", {})
                                if not usuario:
                                    st.warning("Necesitás estar logueado como usuario para enviar consultas.")
                                else:
                                    id_usuario = usuario.get("id_usuario") or usuario.get("ID_usuario")
                                    id_empresa = producto["id_empresa"]
                                    id_producto = producto["id_producto"]

                                    mensaje_sql = mensaje.strip().replace("'", "''")

                                    query_insert = f"""
                                        INSERT INTO consulta (id_usuario, id_empresa, id_producto, mensaje)
                                        VALUES ({id_usuario}, {id_empresa}, {id_producto}, '{mensaje_sql}');
                                    """

                                    success = execute_query(query_insert, is_select=False)
                                    if success:
                                        st.success("Consulta enviada exitosamente.")
                                    else:
                                        st.error("Error al enviar la consulta.")

    # Comparación
    if productos_seleccionados:
        st.markdown("---")
        st.subheader("Comparación de productos seleccionados")
        comparacion_df = pd.DataFrame(productos_seleccionados)[[
            "nombre_producto", "tipo", "material", "precio", "peso_importado", "tiempo_entrega", "stock"
        ]]

        # Renombrar columnas
        comparacion_df = comparacion_df.rename(columns={
            "nombre_producto": "Nombre del producto",
            "tipo": "Tipo",
            "material": "Material",
            "precio": "Precio (ARS)",
            "peso_importado": "Peso (kg)",
            "tiempo_entrega": "Entrega (días)",
            "stock": "Stock disponible"
        })

        # Mostrar tabla con nombres personalizados
        st.dataframe(comparacion_df.set_index("Nombre del producto"))
