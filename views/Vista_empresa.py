import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer
from utils.db import execute_query

def mostrar():
    set_global_styles()
    add_logo_and_header()

    st.title("Vista de Empresa")

    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")  # asegúrate del nombre real

    if not id_empresa:
        st.error("No se encontró la sesión de empresa.")
        return

    st.markdown("## Tus productos")

    # Mostrar últimos productos en formato de cuadrícula (máx. 4)
    productos = execute_query(f"""
        SELECT * FROM producto
        WHERE id_empresa = {id_empresa}
        ORDER BY id_producto DESC
        LIMIT 4
    """)

    if not productos.empty:
        cols = st.columns(2)
        for i, (_, row) in enumerate(productos.iterrows()):
            with cols[i % 2]:
                st.markdown(f"**{row['nombre']}**")
                st.markdown(f"{row['descripcion'][:100]}...")
                st.markdown(f"🧪 Material: {row['material']}  \n💵 ${row['precio']}")
    else:
        st.info("No tenés productos cargados aún.")

    # Botones
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Ver todos mis productos"):
            st.session_state["vista"] = "productos_empresa"
            st.rerun()

    with col2:
        if st.button("➕ Cargar un nuevo producto"):
            st.session_state["vista"] = "cargar_producto"
            st.rerun()

    with col3:
        consulta_tipo = st.selectbox("📬 Ver consultas:", ["Recientes", "Respondidas", "Pendientes"])
        if st.button("Mostrar consultas"):
            st.session_state["vista"] = "consultas_empresa"
            st.session_state["filtro_consulta"] = consulta_tipo
            st.rerun()

    add_footer()
