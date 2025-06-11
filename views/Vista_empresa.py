import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer
from utils.db import execute_query

def mostrar():
    set_global_styles()
    add_logo_and_header()
    
    # CSS personalizado para mejorar la estética
    st.markdown("""
    <style>
    .empresa-header {
        background: linear-gradient(135deg, #7BA7D1 0%, #5A8BC2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .empresa-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .empresa-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .producto-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #7BA7D1;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .producto-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .producto-nombre {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .producto-descripcion {
        color: #7f8c8d;
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    
    .producto-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 1rem;
        border-top: 1px solid #ecf0f1;
    }
    
    .material-tag {
        background: #e8f5e8;
        color: #7BA7D1;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .precio-tag {
        background: #fff3cd;
        color: #856404;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-top: 3px solid #7BA7D1;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2E8B57;
    }
    
    .stat-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .action-button {
        background: linear-gradient(135deg, #7BA7D1 0%, #5A8BC2 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .action-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 167, 209, 0.4);
    }
    
    .back-button {
        background: linear-gradient(135deg, #A8C8E6 0%, #8BBDE0 100%);
        color: #2C5282;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .back-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(168, 200, 230, 0.4);
    }
    
    .no-productos {
        text-align: center;
        padding: 3rem;
        background: #f8f9fa;
        border-radius: 12px;
        border: 2px dashed #dee2e6;
    }
    
    .no-productos-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")
    nombre_empresa = empresa.get("nombre", "Tu Empresa")
    
    if not id_empresa:
        st.error("No se encontró la sesión de empresa.")
        return
    
    # Botón de volver
    if st.button("← Volver", key="volver_inicio", help="Cerrar sesión y volver al inicio"):
        # Limpiar session state de empresa
        if "empresa" in st.session_state:
            del st.session_state["empresa"]
        st.session_state["vista"] = "inicio"
        st.rerun()
    
    # Header de empresa
    st.markdown(f"""
    <div class="empresa-header">
        <div class="empresa-title">¡Bienvenido, {nombre_empresa}!</div>
        <div class="empresa-subtitle">Gestiona tus productos y consultas desde aquí</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Estadísticas rápidas
    total_productos = execute_query(f"""
        SELECT COUNT(*) as total FROM producto WHERE id_empresa = {id_empresa}
    """)
    
    consultas_pendientes = execute_query(f"""
        SELECT COUNT(*) as total FROM consulta c
        JOIN producto p ON c.id_producto = p.id_producto
        WHERE p.id_empresa = {id_empresa} AND c.estado = 'Pendiente'
    """)
    
    productos_activos = execute_query(f"""
        SELECT COUNT(*) as total FROM producto 
        WHERE id_empresa = {id_empresa}
    """)
    
    total_prod = total_productos.iloc[0]['total'] if not total_productos.empty else 0
    consultas_pend = consultas_pendientes.iloc[0]['total'] if not consultas_pendientes.empty else 0
    prod_activos = productos_activos.iloc[0]['total'] if not productos_activos.empty else 0
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{total_prod}</div>
            <div class="stat-label">Total Productos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{prod_activos}</div>
            <div class="stat-label">Productos Activos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{consultas_pend}</div>
            <div class="stat-label">Consultas Pendientes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## Tus Productos Recientes")
    
    # Obtener últimos productos
    productos = execute_query(f"""
        SELECT * FROM producto
        WHERE id_empresa = {id_empresa}
        ORDER BY id_producto DESC
        LIMIT 4
    """)
    
    if not productos.empty:
        # Mostrar productos en formato de tarjetas
        cols = st.columns(2)
        for i, (_, row) in enumerate(productos.iterrows()):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="producto-card">
                    <div class="producto-nombre">{row['nombre']}</div>
                    <div class="producto-descripcion">{row['descripcion'][:100]}{'...' if len(row['descripcion']) > 100 else ''}</div>
                    <div class="producto-info">
                        <span class="material-tag">🧪 {row['material']}</span>
                        <span class="precio-tag">💵 ${row['precio']:,.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="no-productos">
            <div class="no-productos-icon">📦</div>
            <h3>¡Aún no tienes productos!</h3>
            <p>Comienza cargando tu primer producto para que los compradores puedan encontrarte</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sección de acciones principales
    st.markdown("---")
    st.markdown("## Acciones Rápidas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Productos")
        if st.button("Ver todos mis productos", key="ver_productos", help="Administra todos tus productos"):
            st.session_state["vista"] = "productos_empresa"
            st.rerun()
        
        if st.button("➕ Cargar nuevo producto", key="cargar_producto", help="Agregar un producto al catálogo"):
            st.session_state["vista"] = "Cargar_producto"  # ← Solución: mayúsculas como en el archivo principal
            st.rerun()
    
    with col2:
        st.markdown("### Consultas")
        if st.button("Ver consultas", key="ver_consultas"):
            st.session_state["vista"] = "Ver_consultas"
            st.rerun()

    
    with col3:
        st.markdown("### ⚙️ Configuración")
        if st.button("✏️ Editar perfil", key="editar_perfil", help="Actualiza los datos de tu empresa"):
            # Aquí puedes agregar la funcionalidad de editar perfil
            st.info("Funcionalidad próximamente")
        
        if st.button("📈 Estadísticas", key="estadisticas", help="Ve el rendimiento de tus productos"):
            # Aquí puedes agregar la funcionalidad de estadísticas
            st.info("Funcionalidad próximamente")
    
    # Sección de ayuda rápida
    with st.expander("💡 Consejos para mejorar tus ventas"):
        st.markdown("""
        - **Fotos de calidad**: Sube imágenes claras y bien iluminadas de tus productos
        - **Descripciones detalladas**: Incluye materiales, dimensiones y características especiales
        - **Responde rápido**: Contesta las consultas lo antes posible para generar confianza
        - **Precios competitivos**: Investiga el mercado para establecer precios justos
        - **Actualiza regularmente**: Mantén tu catálogo actualizado con nuevos productos
        """)
