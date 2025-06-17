import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query
from views import productos_empresa, Ver_consultas  # Asegurate de que las rutas sean correctas

def mostrar():
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("empresa")

    # CSS personalizado
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
        color: white;
    }

    .empresa-subtitle {
        font-size: 1.2rem;
        opacity: 0.95;
        color: white;
    }

    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
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
    </style>
    """, unsafe_allow_html=True)

    # Cargar datos de la empresa desde session_state
    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")
    nombre_empresa = empresa.get("nombre", "Tu Empresa")

    if not id_empresa:
        st.error("No se encontró la sesión de empresa.")
        return

    # Botón volver
    if st.button("← Volver", key="volver_inicio"):
        del st.session_state["empresa"]
        st.session_state["vista"] = "inicio"
        st.rerun()

    # Cartel de bienvenida con estilo
    st.markdown(f"""
    <div class="empresa-header">
        <div class="empresa-title">¡Bienvenido, {nombre_empresa}!</div>
        <div class="empresa-subtitle">Gestiona tus productos y consultas desde aquí</div>
    </div>
    """, unsafe_allow_html=True)

    # Consultas a la base de datos
    total_productos = execute_query(f"""
        SELECT COUNT(*) as total FROM producto WHERE id_empresa = {id_empresa}
    """)
    productos_activos = execute_query(f"""
        SELECT COUNT(*) as total FROM producto WHERE id_empresa = {id_empresa}
    """)
    consultas_pendientes = execute_query(f"""
        SELECT COUNT(*) as total
        FROM consulta c
        JOIN producto p ON c.id_producto = p.id_producto
        WHERE p.id_empresa = {id_empresa} AND LOWER(TRIM(c.estado_consulta)) = 'pendiente'
    """)


    total_prod = total_productos.iloc[0]['total'] if not total_productos.empty else 0
    prod_activos = productos_activos.iloc[0]['total'] if not productos_activos.empty else 0
    consultas_pend = consultas_pendientes.iloc[0]['total'] if not consultas_pendientes.empty else 0

    # Estadísticas con tarjetas visuales
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

    # Separador visual
    st.markdown("---")
    st.markdown("<h3 style='text-align:center;'>Panel de Control</h3>", unsafe_allow_html=True)

    # Pestañas
    pestañas = st.tabs(["📦 Mis Productos", "📨 Consultas", "⚙️ Configuración"])

    with pestañas[0]:
        productos_empresa.mostrar()

    with pestañas[1]:
        Ver_consultas.mostrar()

    with pestañas[2]:
        st.info("Aquí podés modificar la configuración de tu empresa.")
        st.write(f"**Nombre de la empresa:** {empresa.get('nombre', 'Sin nombre')}")
        st.write(f"**Correo registrado:** {empresa.get('mail', 'Sin correo')}")
        st.markdown("---")
        st.warning("Próximamente vas a poder editar los datos de tu empresa desde aquí.")
