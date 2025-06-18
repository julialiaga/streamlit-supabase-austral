import streamlit as st
from utils.layout import set_global_styles, add_logo_and_header, add_footer, add_page_specific_styles
from utils.db import execute_query
from views import productos_empresa, Ver_consultas, Cargar_producto
import pandas as pd
import time

# Cache para estilos CSS
@st.cache_data
def get_custom_styles():
    """Retorna los estilos CSS personalizados."""
    return """
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
    """

# Cache para estadísticas de la empresa - MODIFICADO para detectar actualizaciones
@st.cache_data(ttl=60, show_spinner=False)
def get_empresa_stats(id_empresa, timestamp=None):
    """Obtiene las estadísticas de la empresa de forma eficiente."""
    try:
        query = f"""
        SELECT 
            (SELECT COUNT(*) FROM producto WHERE id_empresa = {id_empresa}) as total_productos,
            (SELECT COUNT(*) FROM producto WHERE id_empresa = {id_empresa}) as productos_activos,
            (SELECT COUNT(*) 
             FROM consulta c 
             JOIN producto p ON c.id_producto = p.id_producto 
             WHERE p.id_empresa = {id_empresa} 
             AND LOWER(TRIM(c.estado_consulta)) = 'pendiente') as consultas_pendientes
        """

        result = execute_query(query)

        if not result.empty:
            return {
                'total_productos': int(result.iloc[0]['total_productos']),
                'productos_activos': int(result.iloc[0]['productos_activos']),
                'consultas_pendientes': int(result.iloc[0]['consultas_pendientes'])
            }
        else:
            return {
                'total_productos': 0,
                'productos_activos': 0,
                'consultas_pendientes': 0
            }
    except Exception as e:
        st.error(f"Error al obtener estadísticas: {str(e)}")
        return {
            'total_productos': 0,
            'productos_activos': 0,
            'consultas_pendientes': 0
        }

# Cache para validar empresa
@st.cache_data(ttl=300)  # Cache por 5 minutos
def validate_empresa_session():
    """Valida la sesión de empresa."""
    empresa = st.session_state.get("empresa", {})
    id_empresa = empresa.get("id_empresa") or empresa.get("ID_empresa")
    nombre_empresa = empresa.get("nombre", "Tu Empresa")

    return id_empresa, nombre_empresa, empresa

def check_and_refresh_cache():
    """Verifica y actualiza el cache si es necesario"""
    # Verificar si hay señales de actualización
    if (st.session_state.get('refresh_stats', False) or 
        st.session_state.get('force_refresh_empresa', False) or
        st.session_state.get('productos_updated_timestamp', 0) > 0):
        
        # Limpiar caches
        get_empresa_stats.clear()
        
        # Limpiar las señales
        st.session_state.pop('refresh_stats', None)
        st.session_state.pop('force_refresh_empresa', None)
        
        return True
    return False

def render_stats_cards(stats):
    """Renderiza las tarjetas de estadísticas."""
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{stats['total_productos']}</div>
            <div class="stat-label">Total Productos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['productos_activos']}</div>
            <div class="stat-label">Productos Activos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['consultas_pendientes']}</div>
            <div class="stat-label">Consultas Pendientes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_welcome_header(nombre_empresa):
    """Renderiza el header de bienvenida."""
    st.markdown(f"""
    <div class="empresa-header">
        <div class="empresa-title">¡Bienvenido, {nombre_empresa}!</div>
        <div class="empresa-subtitle">Gestiona tus productos y consultas desde aquí</div>
    </div>
    """, unsafe_allow_html=True)

def render_configuration_tab(empresa):
    """Renderiza la pestaña de configuración."""
    st.info("Aquí podés modificar la configuración de tu empresa.")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"*Nombre de la empresa:* {empresa.get('nombre', 'Sin nombre')}")
    with col2:
        st.write(f"*Correo registrado:* {empresa.get('mail', 'Sin correo')}")

    st.markdown("---")
    st.warning("Próximamente vas a poder editar los datos de tu empresa desde aquí.")

def mostrar():
    # Inicialización de estilos (solo una vez)
    set_global_styles()
    add_logo_and_header()
    add_page_specific_styles("empresa")

    # Aplicar estilos CSS cacheados
    st.markdown(get_custom_styles(), unsafe_allow_html=True)

    # Validar sesión de empresa
    id_empresa, nombre_empresa, empresa = validate_empresa_session()

    if not id_empresa:
        st.error("No se encontró la sesión de empresa.")
        return

    # Mostrar mensaje de éxito si existe
    if "mensaje_exito" in st.session_state:
        st.success(st.session_state["mensaje_exito"])
        del st.session_state["mensaje_exito"]

    # Botón volver (con callback optimizado)# Botón de volver
    if st.button("← Volver", key="volver_inicio", help="Cerrar sesión y volver al inicio"):
        # Limpiar cache relacionado con la empresa
        get_empresa_stats.clear()
        validate_empresa_session.clear()

        # Limpiar sesión
        if "empresa" in st.session_state:
            del st.session_state["empresa"]
        if "refresh_stats" in st.session_state:
            del st.session_state["refresh_stats"]
        st.session_state["vista"] = "inicio"
        st.rerun()

    # Renderizar header de bienvenida
    render_welcome_header(nombre_empresa)

    # VERIFICAR Y ACTUALIZAR CACHE SI ES NECESARIO
    cache_was_refreshed = check_and_refresh_cache()

    # Obtener estadísticas con timestamp para forzar actualización
    timestamp = st.session_state.get('productos_updated_timestamp', time.time())
    
    with st.spinner("Cargando estadísticas..."):
        stats = get_empresa_stats(id_empresa, timestamp=timestamp)

    # Renderizar tarjetas de estadísticas
    render_stats_cards(stats)

    # Si el cache fue actualizado, mostrar confirmación visual
    if cache_was_refreshed:
        st.success("✅ Estadísticas actualizadas", icon="🔄")
        time.sleep(0.5)  # Breve pausa para que se vea el mensaje

    # Separador visual
    st.markdown("---")
    st.markdown("<h3 style='text-align:center;'>Panel de Control</h3>", unsafe_allow_html=True)

    # Pestañas optimizadas
    tab1, tab2, tab3, tab4 = st.tabs(["🗂 Mis Productos", "➕ Cargar un nuevo producto", "💬 Consultas", "⚙ Configuración"])

    with tab1:
        with st.container():
            productos_empresa.mostrar()

    with tab2:
        with st.container():
            Cargar_producto.mostrar()

    with tab3:
        with st.container():
            Ver_consultas.mostrar()

    with tab4:
        with st.container():
            render_configuration_tab(empresa)

# Función para limpiar cache cuando sea necesario
def clear_empresa_cache():
    """Limpia el cache relacionado con la empresa."""
    get_empresa_stats.clear()
    validate_empresa_session.clear()
    
    # Agregar señal de actualización
    st.session_state['refresh_stats'] = True