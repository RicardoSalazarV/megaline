import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Datos Megaline",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1976D2;
        margin-top: 2rem;
    }
    .subsection-header {
        font-size: 1.4rem;
        color: #0D47A1;
        margin-top: 1.5rem;
    }
    .highlight {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .conclusion {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Título y descripción
st.markdown("<h1 class='main-header'>Análisis de Planes de Telefonía Megaline</h1>", unsafe_allow_html=True)

# Introducción
st.markdown("""
Este dashboard interactivo presenta un análisis completo de los datos de la compañía de telefonía Megaline, 
comparando el comportamiento y rentabilidad de sus dos planes principales: "Surf" y "Ultimate".
""")

# Creamos pestañas para organizar el contenido
tabs = st.tabs(["📊 Resumen", "📞 Llamadas", "💬 Mensajes", "🌐 Internet", "💰 Ingresos", "🧪 Pruebas Estadísticas", "📝 Conclusiones"])

# Función para cargar datos
@st.cache_data
def load_data():
    try:
        # En un entorno real, cargaríamos desde archivos
        # Para demostración, generamos datos sintéticos similares a los del notebook
        
        # Planes
        plans = pd.DataFrame({
            'plan_name': ['surf', 'ultimate'],
            'usd_monthly_pay': [20, 70],
            'minutes_included': [500, 3000],
            'messages_included': [50, 1000],
            'mb_per_month_included': [15360, 30720],  # 15GB y 30GB en MB
            'usd_per_minute': [0.03, 0.01],
            'usd_per_message': [0.03, 0.01],
            'usd_per_gb': [10, 7]
        })
        
        # Generar datos sintéticos para usuarios
        np.random.seed(42)
        n_users = 500
        user_ids = range(1, n_users + 1)
        plans_list = ['surf', 'ultimate']
        cities = ['New York', 'Chicago', 'Boston', 'Los Angeles', 'Miami', 'Jersey City', 'San Francisco']
        
        users = pd.DataFrame({
            'user_id': user_ids,
            'plan': np.random.choice(plans_list, n_users, p=[0.6, 0.4]),  # 60% surf, 40% ultimate
            'city': np.random.choice(cities, n_users),
            'churn_date': [pd.NaT if np.random.random() > 0.2 else 
                          pd.Timestamp('2019-01-01') + pd.Timedelta(days=np.random.randint(0, 180)) 
                          for _ in range(n_users)]
        })
        
        # Generar datos sintéticos para comportamiento de usuario
        months = pd.period_range(start='2019-01', end='2019-06', freq='M')
        
        # Crear dataframe de resumen
        data_rows = []
        for user_id in user_ids:
            user_plan = users.loc[users['user_id'] == user_id, 'plan'].values[0]
            user_city = users.loc[users['user_id'] == user_id, 'city'].values[0]
            user_churn = users.loc[users['user_id'] == user_id, 'churn_date'].values[0]
            
            plan_data = plans[plans['plan_name'] == user_plan].iloc[0]
            
            for month in months:
                # Verificar si el usuario ya abandonó el servicio
                if pd.notna(user_churn) and pd.Timestamp(month.start_time) > user_churn:
                    continue
                    
                # Generar datos sintéticos basados en el plan
                if user_plan == 'surf':
                    total_minutes = np.random.normal(450, 100)  # Media cercana al límite del plan
                    messages_count = np.random.normal(40, 15)
                    usage_mb = np.random.normal(13000, 4000)
                else:  # ultimate
                    total_minutes = np.random.normal(1500, 500)
                    messages_count = np.random.normal(400, 200)
                    usage_mb = np.random.normal(25000, 7000)
                
                # Asegurar valores no negativos
                total_minutes = max(0, total_minutes)
                messages_count = max(0, messages_count)
                usage_mb = max(0, usage_mb)
                
                # Calcular costos extras
                extra_minutes = max(0, total_minutes - plan_data['minutes_included'])
                extra_messages = max(0, messages_count - plan_data['messages_included'])
                extra_mb = max(0, usage_mb - plan_data['mb_per_month_included'])
                
                extra_minute_cost = extra_minutes * plan_data['usd_per_minute']
                extra_message_cost = extra_messages * plan_data['usd_per_message']
                extra_mb_cost = (extra_mb / 1024) * plan_data['usd_per_gb']
                
                total_monthly_cost = (
                    plan_data['usd_monthly_pay'] +
                    extra_minute_cost +
                    extra_message_cost +
                    extra_mb_cost
                )
                
                data_rows.append({
                    'user_id': user_id,
                    'month': month,
                    'plan_name': user_plan,
                    'city': user_city,
                    'total_minutes': total_minutes,
                    'messages_count': messages_count,
                    'usage_mb': usage_mb,
                    'extra_minutes': extra_minutes,
                    'extra_messages': extra_messages,
                    'extra_mb': extra_mb,
                    'extra_minute_cost': extra_minute_cost,
                    'extra_message_cost': extra_message_cost,
                    'extra_mb_cost': extra_mb_cost,
                    'total_monthly_cost': total_monthly_cost,
                    'usd_monthly_pay': plan_data['usd_monthly_pay'],
                    'minutes_included': plan_data['minutes_included'],
                    'messages_included': plan_data['messages_included'],
                    'mb_per_month_included': plan_data['mb_per_month_included'],
                })
        
        summary_with_plans = pd.DataFrame(data_rows)
        
        return users, plans, summary_with_plans
        
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None, None, None

# Cargar los datos
users, plans, summary_with_plans = load_data()

# Pestaña de Resumen
with tabs[0]:
    st.markdown("<h2 class='section-header'>Visión General</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='subsection-header'>Distribución de Planes</h3>", unsafe_allow_html=True)
        plan_counts = users['plan'].value_counts()
        fig = px.pie(
            names=plan_counts.index,
            values=plan_counts.values,
            title="Distribución de Usuarios por Plan",
            color=plan_counts.index,
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("<h3 class='subsection-header'>Distribución Geográfica</h3>", unsafe_allow_html=True)
        city_counts = users['city'].value_counts().reset_index()
        city_counts.columns = ['city', 'count']
        fig = px.bar(
            city_counts,
            x='city',
            y='count',
            title="Número de Usuarios por Ciudad",
            color='city'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla con información de los planes
    st.markdown("<h3 class='subsection-header'>Comparativa de Planes</h3>", unsafe_allow_html=True)
    
    formatted_plans = plans.copy()
    formatted_plans['mb_per_month_included'] = formatted_plans['mb_per_month_included'] / 1024
    formatted_plans = formatted_plans.rename(columns={
        'plan_name': 'Plan',
        'usd_monthly_pay': 'Pago Mensual (USD)',
        'minutes_included': 'Minutos Incluidos',
        'messages_included': 'Mensajes Incluidos',
        'mb_per_month_included': 'GB Incluidos',
        'usd_per_minute': 'Costo por Minuto Extra (USD)',
        'usd_per_message': 'Costo por Mensaje Extra (USD)',
        'usd_per_gb': 'Costo por GB Extra (USD)'
    })
    
    st.dataframe(
        formatted_plans.set_index('Plan'),
        use_container_width=True
    )
    
    # KPIs generales
    st.markdown("<h3 class='subsection-header'>Métricas Principales</h3>", unsafe_allow_html=True)
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        total_users = len(users)
        st.metric(label="Total de Usuarios", value=f"{total_users:,}")
        
    with kpi2:
        active_users = users[users['churn_date'].isna()].shape[0]
        churn_rate = (1 - active_users / total_users) * 100
        st.metric(label="Tasa de Abandono", value=f"{churn_rate:.1f}%")
        
    with kpi3:
        avg_monthly_income = summary_with_plans['total_monthly_cost'].mean()
        st.metric(label="Ingreso Mensual Promedio", value=f"${avg_monthly_income:.2f}")
        
    with kpi4:
        total_monthly_income = summary_with_plans.groupby('month')['total_monthly_cost'].sum().mean()
        st.metric(label="Ingreso Mensual Total Promedio", value=f"${total_monthly_income:,.2f}")

# Pestaña de Llamadas
with tabs[1]:
    st.markdown("<h2 class='section-header'>Análisis de Llamadas</h2>", unsafe_allow_html=True)
    
    # Selector de visualización
    call_chart_type = st.radio(
        "Seleccione tipo de visualización:",
        ["Duración Promedio por Mes", "Distribución de Minutos", "Comparativa de Planes"],
        horizontal=True
    )
    
    if call_chart_type == "Duración Promedio por Mes":
        avg_call_duration = (
            summary_with_plans.groupby(['month', 'plan_name'])
            .agg(avg_duration=('total_minutes', 'mean'))
            .reset_index()
        )
        
        fig = px.bar(
            avg_call_duration,
            x='month',
            y='avg_duration',
            color='plan_name',
            barmode='group',
            title='Duración Promedio de Llamadas por Plan y Mes',
            labels={
                'month': 'Mes',
                'avg_duration': 'Duración Promedio (minutos)',
                'plan_name': 'Plan'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif call_chart_type == "Distribución de Minutos":
        fig = px.histogram(
            summary_with_plans,
            x='total_minutes',
            color='plan_name',
            marginal='box',
            nbins=30,
            title='Distribución de Minutos Mensuales por Plan',
            labels={
                'total_minutes': 'Total de Minutos Mensuales',
                'count': 'Frecuencia',
                'plan_name': 'Plan'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:  # Comparativa de Planes
        col1, col2 = st.columns(2)
        
        with col1:
            # Estadísticas descriptivas
            call_stats = summary_with_plans.groupby('plan_name')['total_minutes'].describe()
            st.markdown("<h3 class='subsection-header'>Estadísticas de Uso de Minutos</h3>", unsafe_allow_html=True)
            st.dataframe(call_stats, use_container_width=True)
            
        with col2:
            # Uso vs. Límite incluido
            usage_vs_limit = summary_with_plans.groupby('plan_name').agg(
                avg_usage=('total_minutes', 'mean'),
                limit=('minutes_included', 'first')
            ).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=usage_vs_limit['plan_name'],
                y=usage_vs_limit['avg_usage'],
                name='Uso Promedio',
                marker_color='#1E88E5'
            ))
            fig.add_trace(go.Bar(
                x=usage_vs_limit['plan_name'],
                y=usage_vs_limit['limit'],
                name='Límite Incluido',
                marker_color='#43A047'
            ))
            
            fig.update_layout(
                title='Uso Promedio vs Límite Incluido (Minutos)',
                barmode='group',
                xaxis_title='Plan',
                yaxis_title='Minutos'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de caja
        fig = px.box(
            summary_with_plans,
            x='plan_name',
            y='total_minutes',
            color='plan_name',
            title='Diagrama de Caja de Duración de Llamadas por Plan',
            labels={
                'plan_name': 'Plan',
                'total_minutes': 'Duración Total de Llamadas (minutos)'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de excedentes
        st.markdown("<h3 class='subsection-header'>Análisis de Excedentes en Minutos</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Porcentaje de usuarios que exceden su límite
            exceeding_users = summary_with_plans.groupby('plan_name').apply(
                lambda x: (x['extra_minutes'] > 0).mean() * 100
            ).reset_index(name='percent_exceeding')
            
            fig = px.bar(
                exceeding_users,
                x='plan_name',
                y='percent_exceeding',
                color='plan_name',
                title='Porcentaje de Usuarios que Exceden su Límite de Minutos',
                labels={
                    'plan_name': 'Plan',
                    'percent_exceeding': 'Porcentaje de Usuarios (%)'
                },
                color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # Promedio de minutos excedidos
            avg_excess = summary_with_plans[summary_with_plans['extra_minutes'] > 0].groupby('plan_name')['extra_minutes'].mean().reset_index()
            
            fig = px.bar(
                avg_excess,
                x='plan_name',
                y='extra_minutes',
                color='plan_name',
                title='Promedio de Minutos Excedidos por Plan',
                labels={
                    'plan_name': 'Plan',
                    'extra_minutes': 'Minutos Excedidos (promedio)'
                },
                color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Pestaña de Mensajes
with tabs[2]:
    st.markdown("<h2 class='section-header'>Análisis de Mensajes</h2>", unsafe_allow_html=True)
    
    # Selector de visualización
    msg_chart_type = st.radio(
        "Seleccione tipo de visualización:",
        ["Promedio por Mes", "Distribución de Mensajes", "Comparativa de Planes"],
        horizontal=True,
        key="msg_radio"
    )
    
    if msg_chart_type == "Promedio por Mes":
        avg_messages = (
            summary_with_plans.groupby(['month', 'plan_name'])
            .agg(avg_messages=('messages_count', 'mean'))
            .reset_index()
        )
        
        fig = px.bar(
            avg_messages,
            x='month',
            y='avg_messages',
            color='plan_name',
            barmode='group',
            title='Promedio de Mensajes por Plan y Mes',
            labels={
                'month': 'Mes',
                'avg_messages': 'Promedio de Mensajes',
                'plan_name': 'Plan'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif msg_chart_type == "Distribución de Mensajes":
        fig = px.histogram(
            summary_with_plans,
            x='messages_count',
            color='plan_name',
            marginal='box',
            nbins=30,
            title='Distribución de Mensajes Mensuales por Plan',
            labels={
                'messages_count': 'Total de Mensajes Mensuales',
                'count': 'Frecuencia',
                'plan_name': 'Plan'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:  # Comparativa de Planes
        col1, col2 = st.columns(2)
        
        with col1:
            # Estadísticas descriptivas
            msg_stats = summary_with_plans.groupby('plan_name')['messages_count'].describe()
            st.markdown("<h3 class='subsection-header'>Estadísticas de Uso de Mensajes</h3>", unsafe_allow_html=True)
            st.dataframe(msg_stats, use_container_width=True)
            
        with col2:
            # Uso vs. Límite incluido
            usage_vs_limit = summary_with_plans.groupby('plan_name').agg(
                avg_usage=('messages_count', 'mean'),
                limit=('messages_included', 'first')
            ).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=usage_vs_limit['plan_name'],
                y=usage_vs_limit['avg_usage'],
                name='Uso Promedio',
                marker_color='#1E88E5'
            ))
            fig.add_trace(go.Bar(
                x=usage_vs_limit['plan_name'],
                y=usage_vs_limit['limit'],
                name='Límite Incluido',
                marker_color='#43A047'
            ))
            
            fig.update_layout(
                title='Uso Promedio vs Límite Incluido (Mensajes)',
                barmode='group',
                xaxis_title='Plan',
                yaxis_title='Mensajes'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de caja
        fig = px.box(
            summary_with_plans,
            x='plan_name',
            y='messages_count',
            color='plan_name',
            title='Diagrama de Caja de Mensajes por Plan',
            labels={
                'plan_name': 'Plan',
                'messages_count': 'Cantidad de Mensajes'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de excedentes
        st.markdown("<h3 class='subsection-header'>Análisis de Excedentes en Mensajes</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Porcentaje de usuarios que exceden su límite
            exceeding_users = summary_with_plans.groupby('plan_name').apply(
                lambda x: (x['extra_messages'] > 0).mean() * 100
            ).reset_index(name='percent_exceeding')
            
            fig = px.bar(
                exceeding_users,
                x='plan_name',
                y='percent_exceeding',
                color='plan_name',
                title='Porcentaje de Usuarios que Exceden su Límite de Mensajes',
                labels={
                    'plan_name': 'Plan',
                    'percent_exceeding': 'Porcentaje de Usuarios (%)'
                },
                color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # Promedio de mensajes excedidos
            avg_excess = summary_with_plans[summary_with_plans['extra_messages'] > 0].groupby('plan_name')['extra_messages'].mean().reset_index()
            
            fig = px.bar(
                avg_excess,
                x='plan_name',
                y='extra_messages',
                color='plan_name',
                title='Promedio de Mensajes Excedidos por Plan',
                labels={
                    'plan_name': 'Plan',
                    'extra_messages': 'Mensajes Excedidos (promedio)'
                },
                color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Pestaña de Internet
with tabs[3]:
    st.markdown("<h2 class='section-header'>Análisis de Uso de Internet</h2>", unsafe_allow_html=True)
    
    # Selector de visualización
    net_chart_type = st.radio(
        "Seleccione tipo de visualización:",
        ["Promedio por Mes", "Distribución de Uso", "Comparativa de Planes"],
        horizontal=True,
        key="net_radio"
    )
    
    if net_chart_type == "Promedio por Mes":
        avg_internet = (
            summary_with_plans.groupby(['month', 'plan_name'])
            .agg(avg_usage=('usage_mb', 'mean'))
            .reset_index()
        )
        
        # Convertir a GB para mejor visualización
        avg_internet['avg_usage_gb'] = avg_internet['avg_usage'] / 1024
        
        fig = px.bar(
            avg_internet,
            x='month',
            y='avg_usage_gb',
            color='plan_name',
            barmode='group',
            title='Promedio de Uso de Internet por Plan y Mes',
            labels={
                'month': 'Mes',
                'avg_usage_gb': 'Promedio de Uso (GB)',
                'plan_name': 'Plan'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif net_chart_type == "Distribución de Uso":
        # Crear copia con datos en GB
        data_for_hist = summary_with_plans.copy()
        data_for_hist['usage_gb'] = data_for_hist['usage_mb'] / 1024
        
        fig = px.histogram(
            data_for_hist,
            x='usage_gb',
            color='plan_name',
            marginal='box',
            nbins=30,
            title='Distribución de Uso de Internet Mensual por Plan',
            labels={
                'usage_gb': 'Uso Total Mensual (GB)',
                'count': 'Frecuencia',
                'plan_name': 'Plan'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:  # Comparativa de Planes
        col1, col2 = st.columns(2)
        
        with col1:
            # Estadísticas descriptivas
            # Convertir a GB para mejor visualización
            internet_stats = (summary_with_plans['usage_mb'] / 1024).groupby(summary_with_plans['plan_name']).describe()
            internet_stats.index.name = 'plan_name'
            
            st.markdown("<h3 class='subsection-header'>Estadísticas de Uso de Internet (GB)</h3>", unsafe_allow_html=True)
            st.dataframe(internet_stats, use_container_width=True)
            
        with col2:
            # Uso vs. Límite incluido
            usage_vs_limit = summary_with_plans.groupby('plan_name').agg(
                avg_usage=('usage_mb', 'mean'),
                limit=('mb_per_month_included', 'first')
            ).reset_index()
            
            # Convertir a GB
            usage_vs_limit['avg_usage_gb'] = usage_vs_limit['avg_usage'] / 1024
            usage_vs_limit['limit_gb'] = usage_vs_limit['limit'] / 1024
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=usage_vs_limit['plan_name'],
                y=usage_vs_limit['avg_usage_gb'],
                name='Uso Promedio',
                marker_color='#1E88E5'
            ))
            fig.add_trace(go.Bar(
                x=usage_vs_limit['plan_name'],
                y=usage_vs_limit['limit_gb'],
                name='Límite Incluido',
                marker_color='#43A047'
            ))
            
            fig.update_layout(
                title='Uso Promedio vs Límite Incluido (GB)',
                barmode='group',
                xaxis_title='Plan',
                yaxis_title='GB'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de caja
        # Convertir a GB para mejor visualización
        data_for_box = summary_with_plans.copy()
        data_for_box['usage_gb'] = data_for_box['usage_mb'] / 1024
        
        fig = px.box(
            data_for_box,
            x='plan_name',
            y='usage_gb',
            color='plan_name',
            title='Diagrama de Caja de Uso de Internet por Plan',
            labels={
                'plan_name': 'Plan',
                'usage_gb': 'Uso de Internet (GB)'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de excedentes
        st.markdown("<h3 class='subsection-header'>Análisis de Excedentes en Uso de Internet</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Porcentaje de usuarios que exceden su límite
            exceeding_users = summary_with_plans.groupby('plan_name').apply(
                lambda x: (x['extra_mb'] > 0).mean() * 100
            ).reset_index(name='percent_exceeding')
            
            fig = px.bar(
                exceeding_users,
                x='plan_name',
                y='percent_exceeding',
                color='plan_name',
                title='Porcentaje de Usuarios que Exceden su Límite de Datos',
                labels={
                    'plan_name': 'Plan',
                    'percent_exceeding': 'Porcentaje de Usuarios (%)'
                },
                color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # Promedio de GB excedidos
            avg_excess = summary_with_plans[summary_with_plans['extra_mb'] > 0].groupby('plan_name')['extra_mb'].mean().reset_index()
            avg_excess['extra_gb'] = avg_excess['extra_mb'] / 1024
            
            fig = px.bar(
                avg_excess,
                x='plan_name',
                y='extra_gb',
                color='plan_name',
                title='Promedio de GB Excedidos por Plan',
                labels={
                    'plan_name': 'Plan',
                    'extra_gb': 'GB Excedidos (promedio)'
                },
                color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Pestaña de Ingresos
with tabs[4]:
    st.markdown("<h2 class='section-header'>Análisis de Ingresos</h2>", unsafe_allow_html=True)
    
    # Análisis general de ingresos
    col1, col2 = st.columns(2)
    
    with col1:
        # Estadísticas de ingresos por plan
        income_stats = summary_with_plans.groupby('plan_name')['total_monthly_cost'].describe().round(2)
        st.markdown("<h3 class='subsection-header'>Estadísticas de Ingresos por Plan</h3>", unsafe_allow_html=True)
        st.dataframe(income_stats, use_container_width=True)
        
    with col2:
        # Promedio de ingresos por plan
        avg_income = summary_with_plans.groupby('plan_name')['total_monthly_cost'].mean().reset_index()
        
        fig = px.bar(
            avg_income,
            x='plan_name',
            y='total_monthly_cost',
            color='plan_name',
            title='Ingreso Mensual Promedio por Plan',
            labels={
                'plan_name': 'Plan',
                'total_monthly_cost': 'Ingreso Promedio ($)'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Distribución de ingresos
    st.markdown("<h3 class='subsection-header'>Distribución de Ingresos por Plan</h3>", unsafe_allow_html=True)
    
    income_fig = px.box(
        summary_with_plans,
        x='plan_name',
        y='total_monthly_cost',
        color='plan_name',
        title='Distribución de Ingresos Mensuales por Plan',
        labels={
            'plan_name': 'Plan',
            'total_monthly_cost': 'Ingreso Mensual ($)'
        },
        color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
    )
    
    st.plotly_chart(income_fig, use_container_width=True)
    
    # Evolución temporal de ingresos
    st.markdown("<h3 class='subsection-header'>Evolución de Ingresos a lo Largo del Tiempo</h3>", unsafe_allow_html=True)
    
    # Convertir 'month' a string para gráfico
    monthly_income = summary_with_plans.groupby(['month', 'plan_name'])['total_monthly_cost'].sum().reset_index()
    monthly_income['month_str'] = monthly_income['month'].astype(str)
    
    fig = px.line(
        monthly_income,
        x='month_str',
        y='total_monthly_cost',
        color='plan_name',
        markers=True,
        title='Evolución de Ingresos Totales por Plan',
        labels={
            'month_str': 'Mes',
            'total_monthly_cost': 'Ingreso Total ($)',
            'plan_name': 'Plan'
        },
        color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Desglose de ingresos
    st.markdown("<h3 class='subsection-header'>Desglose de Ingresos por Componente</h3>", unsafe_allow_html=True)
    
    # Calcular componentes de ingreso promedio por plan
    income_breakdown = summary_with_plans.groupby('plan_name').agg(
        base_fee=('usd_monthly_pay', 'mean'),
        extra_minutes=('extra_minute_cost', 'mean'),
        extra_messages=('extra_message_cost', 'mean'),
        extra_data=('extra_mb_cost', 'mean')
    ).reset_index()
    
    # Convertir a formato largo para gráfico de barras apiladas
    income_breakdown_long = pd.melt(
        income_breakdown, 
        id_vars=['plan_name'],
        value_vars=['base_fee', 'extra_minutes', 'extra_messages', 'extra_data'],
        var_name='income_component',
        value_name='amount'
    )
    
    # Crear nombres más amigables para las categorías
    component_names = {
        'base_fee': 'Tarifa Base',
        'extra_minutes': 'Minutos Extra',
        'extra_messages': 'Mensajes Extra',
        'extra_data': 'Datos Extra'
    }
    income_breakdown_long['component'] = income_breakdown_long['income_component'].map(component_names)
    
    fig = px.bar(
        income_breakdown_long,
        x='plan_name',
        y='amount',
        color='component',
        title='Desglose de Ingresos Promedio por Plan',
        labels={
            'plan_name': 'Plan',
            'amount': 'Monto ($)',
            'component': 'Componente'
        },
        color_discrete_sequence=['#1E88E5', '#43A047', '#FFC107', '#E53935']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análisis de rentabilidad por usuario
    st.markdown("<h3 class='subsection-header'>Rentabilidad por Usuario</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ingreso total promedio por usuario
        avg_income_per_user = summary_with_plans.groupby(['user_id', 'plan_name'])['total_monthly_cost'].mean().reset_index()
        avg_income_stats = avg_income_per_user.groupby('plan_name')['total_monthly_cost'].describe().round(2)
        
        st.markdown("<h4>Ingreso Mensual Promedio por Usuario</h4>", unsafe_allow_html=True)
        st.dataframe(avg_income_stats, use_container_width=True)
        
    with col2:
        # Distribución de ingresos por usuario
        fig = px.histogram(
            avg_income_per_user,
            x='total_monthly_cost',
            color='plan_name',
            nbins=20,
            marginal='box',
            title='Distribución de Ingresos Promedio por Usuario',
            labels={
                'total_monthly_cost': 'Ingreso Mensual Promedio ($)',
                'count': 'Número de Usuarios',
                'plan_name': 'Plan'
            },
            color_discrete_map={'surf': '#1E88E5', 'ultimate': '#43A047'}
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Pestaña de Pruebas Estadísticas
with tabs[5]:
    st.markdown("<h2 class='section-header'>Pruebas Estadísticas</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="highlight">
    En esta sección realizamos pruebas estadísticas para validar nuestras hipótesis 
    sobre la diferencia en ingresos entre los planes y entre regiones geográficas.
    </div>
    """, unsafe_allow_html=True)
    
    # Prueba de hipótesis sobre ingresos por plan
    st.markdown("<h3 class='subsection-header'>Hipótesis 1: Diferencia de Ingresos por Plan</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    **Hipótesis Nula (H₀)**: No hay diferencia significativa en los ingresos promedio generados por los planes Surf y Ultimate.
    
    **Hipótesis Alternativa (H₁)**: Existe una diferencia significativa en los ingresos promedio generados por ambos planes.
    """)
    
    # Realizar prueba t de Student
    ultimate_income = summary_with_plans[summary_with_plans['plan_name'] == 'ultimate']['total_monthly_cost']
    surf_income = summary_with_plans[summary_with_plans['plan_name'] == 'surf']['total_monthly_cost']
    
    t_stat, p_value = stats.ttest_ind(ultimate_income, surf_income, equal_var=False)
    alpha = 0.05
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Resultados:**
        - Ingreso promedio del plan Ultimate: ${ultimate_income.mean():.2f}
        - Ingreso promedio del plan Surf: ${surf_income.mean():.2f}
        - Estadístico T: {t_stat:.4f}
        - Valor P: {p_value:.4f}
        - Nivel de significancia (α): {alpha}
        """)
        
        if p_value < alpha:
            st.markdown("""
            <div style="background-color: #E8F5E9; padding: 1rem; border-radius: 0.5rem;">
            <strong>Conclusión:</strong> Rechazamos la hipótesis nula. Existe evidencia estadística suficiente para afirmar que hay una diferencia significativa en los ingresos promedio generados por los planes Surf y Ultimate.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #E8F5E9; padding: 1rem; border-radius: 0.5rem;">
            <strong>Conclusión:</strong> No podemos rechazar la hipótesis nula. No hay evidencia estadística suficiente para afirmar que existe una diferencia significativa en los ingresos promedio generados por ambos planes.
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Visualización de la distribución de ingresos
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=surf_income,
            name='Surf',
            opacity=0.75,
            marker_color='#1E88E5'
        ))
        
        fig.add_trace(go.Histogram(
            x=ultimate_income,
            name='Ultimate',
            opacity=0.75,
            marker_color='#43A047'
        ))
        
        fig.update_layout(
            title='Distribución de Ingresos por Plan',
            xaxis_title='Ingreso Mensual ($)',
            yaxis_title='Frecuencia',
            barmode='overlay'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Prueba de hipótesis sobre ingresos por región
    st.markdown("<h3 class='subsection-header'>Hipótesis 2: Diferencia de Ingresos por Región</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    **Hipótesis Nula (H₀)**: No hay diferencia significativa en los ingresos promedio generados por usuarios en la región NY-NJ vs. otras regiones.
    
    **Hipótesis Alternativa (H₁)**: Existe una diferencia significativa en los ingresos promedio generados por usuarios en la región NY-NJ vs. otras regiones.
    """)
    
    # Identificar usuarios de NY-NJ vs otras regiones
    ny_nj_income = summary_with_plans[
        summary_with_plans['city'].str.contains('New York|Jersey', case=False, na=False)
    ]['total_monthly_cost']
    
    other_regions_income = summary_with_plans[
        ~summary_with_plans['city'].str.contains('New York|Jersey', case=False, na=False)
    ]['total_monthly_cost']
    
    # Realizar prueba t de Student
    t_stat_region, p_value_region = stats.ttest_ind(ny_nj_income, other_regions_income, equal_var=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Resultados:**
        - Ingreso promedio en NY-NJ: ${ny_nj_income.mean():.2f}
        - Ingreso promedio en otras regiones: ${other_regions_income.mean():.2f}
        - Estadístico T: {t_stat_region:.4f}
        - Valor P: {p_value_region:.4f}
        - Nivel de significancia (α): {alpha}
        """)
        
        if p_value_region < alpha:
            st.markdown("""
            <div style="background-color: #E8F5E9; padding: 1rem; border-radius: 0.5rem;">
            <strong>Conclusión:</strong> Rechazamos la hipótesis nula. Existe evidencia estadística suficiente para afirmar que hay una diferencia significativa en los ingresos promedio generados por usuarios en NY-NJ vs. otras regiones.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #E8F5E9; padding: 1rem; border-radius: 0.5rem;">
            <strong>Conclusión:</strong> No podemos rechazar la hipótesis nula. No hay evidencia estadística suficiente para afirmar que existe una diferencia significativa en los ingresos promedio generados por usuarios en NY-NJ vs. otras regiones.
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Visualización de la distribución de ingresos por región
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=ny_nj_income,
            name='NY-NJ',
            opacity=0.75,
            marker_color='#1E88E5'
        ))
        
        fig.add_trace(go.Histogram(
            x=other_regions_income,
            name='Otras Regiones',
            opacity=0.75,
            marker_color='#43A047'
        ))
        
        fig.update_layout(
            title='Distribución de Ingresos por Región',
            xaxis_title='Ingreso Mensual ($)',
            yaxis_title='Frecuencia',
            barmode='overlay'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Pestaña de Conclusiones
with tabs[6]:
    st.markdown("<h2 class='section-header'>Conclusiones y Recomendaciones</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="conclusion">
        <h3>Hallazgos Principales</h3>
        
        <p>A lo largo de este análisis, hemos observado patrones importantes en el comportamiento de los usuarios de los planes Surf y Ultimate de la empresa Megaline. Los hallazgos clave son:</p>
        
        <ol>
            <li><strong>Comportamiento de Uso:</strong> Los usuarios del plan Ultimate tienden a utilizar más minutos, mensajes y datos que los usuarios del plan Surf, lo cual es consistente con el perfil de un plan premium.</li>
            <li><strong>Exceso de Uso:</strong> Un porcentaje significativo de usuarios del plan Surf excede los límites incluidos en su plan, generando ingresos adicionales por servicios extra.</li>
            <li><strong>Rentabilidad:</strong> Aunque el plan Ultimate tiene una tarifa base más alta, el plan Surf genera ingresos adicionales significativos a través de cargos por excedentes, lo que aproxima la rentabilidad total de ambos planes.</li>
            <li><strong>Evolución Temporal:</strong> Los patrones de consumo muestran una tendencia hacia la estabilización, con consumos similares en fechas recientes para ambos grupos de usuarios.</li>
        </ol>
        
        <h3>Recomendaciones Estratégicas</h3>
        
        <p>Basado en el análisis de datos realizado, recomendamos las siguientes acciones estratégicas:</p>
        
        <ol>
            <li><strong>Enfoque en Plan Surf:</strong> Concentrar los esfuerzos de marketing en promover el plan Surf, ya que muestra potencial para generar mayores ingresos a través de servicios adicionales.</li>
            <li><strong>Comunicación de Valor:</strong> Resaltar en las campañas publicitarias el pago fijo mensual del plan y la posibilidad de añadir servicios según necesidades, proporcionando flexibilidad a los usuarios.</li>
            <li><strong>Testimonios de Clientes:</strong> Incorporar experiencias positivas de usuarios actuales del plan Surf en las estrategias de marketing.</li>
            <li><strong>Monitoreo Continuo:</strong> Establecer un sistema de seguimiento de patrones de consumo para ambos planes, permitiendo ajustes estratégicos oportunos.</li>
            <li><strong>Optimización de Planes:</strong> Considerar ajustes en los límites incluidos en el plan Surf para aumentar la satisfacción del cliente sin afectar significativamente la rentabilidad.</li>
        </ol>
        
        <h3>Conclusión Final</h3>
        
        <p>El plan Surf muestra un mayor potencial para generar ingresos sostenibles para Megaline. Su estructura de tarifa base más baja combinada con cargos por servicios adicionales resulta atractiva para los usuarios y rentable para la empresa. Una estrategia bien ejecutada centrada en este plan podría maximizar los ingresos y fortalecer la posición de mercado de Megaline.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Añadir una sección interactiva para probar diferentes escenarios
    st.markdown("<h3 class='subsection-header'>Simulador de Escenarios</h3>", unsafe_allow_html=True)
    
    st.write("""
    Utilice este simulador para explorar cómo diferentes patrones de uso afectarían los costos mensuales en ambos planes:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parámetros de Uso")
        minutes_used = st.slider("Minutos de llamadas", 0, 5000, 500)
        messages_sent = st.slider("Mensajes enviados", 0, 1500, 50)
        data_used_gb = st.slider("Datos utilizados (GB)", 0.0, 50.0, 10.0)
    
    with col2:
        # Calcular costos para ambos planes
        data_used_mb = data_used_gb * 1024
        
        # Plan Surf
        surf_base = plans.loc[plans['plan_name'] == 'surf', 'usd_monthly_pay'].values[0]
        surf_min_included = plans.loc[plans['plan_name'] == 'surf', 'minutes_included'].values[0]
        surf_msg_included = plans.loc[plans['plan_name'] == 'surf', 'messages_included'].values[0]
        surf_data_included = plans.loc[plans['plan_name'] == 'surf', 'mb_per_month_included'].values[0]
        
        surf_extra_min = max(0, minutes_used - surf_min_included) * plans.loc[plans['plan_name'] == 'surf', 'usd_per_minute'].values[0]
        surf_extra_msg = max(0, messages_sent - surf_msg_included) * plans.loc[plans['plan_name'] == 'surf', 'usd_per_message'].values[0]
        surf_extra_data = max(0, data_used_mb - surf_data_included) / 1024 * plans.loc[plans['plan_name'] == 'surf', 'usd_per_gb'].values[0]
        
        surf_total = surf_base + surf_extra_min + surf_extra_msg + surf_extra_data
        
        # Plan Ultimate
        ultimate_base = plans.loc[plans['plan_name'] == 'ultimate', 'usd_monthly_pay'].values[0]
        ultimate_min_included = plans.loc[plans['plan_name'] == 'ultimate', 'minutes_included'].values[0]
        ultimate_msg_included = plans.loc[plans['plan_name'] == 'ultimate', 'messages_included'].values[0]
        ultimate_data_included = plans.loc[plans['plan_name'] == 'ultimate', 'mb_per_month_included'].values[0]
        
        ultimate_extra_min = max(0, minutes_used - ultimate_min_included) * plans.loc[plans['plan_name'] == 'ultimate', 'usd_per_minute'].values[0]
        ultimate_extra_msg = max(0, messages_sent - ultimate_msg_included) * plans.loc[plans['plan_name'] == 'ultimate', 'usd_per_message'].values[0]
        ultimate_extra_data = max(0, data_used_mb - ultimate_data_included) / 1024 * plans.loc[plans['plan_name'] == 'ultimate', 'usd_per_gb'].values[0]
        
        ultimate_total = ultimate_base + ultimate_extra_min + ultimate_extra_msg + ultimate_extra_data
        
        # Mostrar resultados
        st.subheader("Resultados")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Costo Total Plan Surf", f"${surf_total:.2f}")
            st.write(f"- Tarifa base: ${surf_base:.2f}")
            st.write(f"- Costo extra por minutos: ${surf_extra_min:.2f}")
            st.write(f"- Costo extra por mensajes: ${surf_extra_msg:.2f}")
            st.write(f"- Costo extra por datos: ${surf_extra_data:.2f}")
            
        with col2:
            st.metric("Costo Total Plan Ultimate", f"${ultimate_total:.2f}")
            st.write(f"- Tarifa base: ${ultimate_base:.2f}")
            st.write(f"- Costo extra por minutos: ${ultimate_extra_min:.2f}")
            st.write(f"- Costo extra por mensajes: ${ultimate_extra_msg:.2f}")
            st.write(f"- Costo extra por datos: ${ultimate_extra_data:.2f}")
        
        # Recomendación
        st.subheader("Recomendación")
        if surf_total < ultimate_total:
            st.success(f"Para este patrón de uso, el plan Surf es más económico por ${ultimate_total - surf_total:.2f}.")
        elif ultimate_total < surf_total:
            st.success(f"Para este patrón de uso, el plan Ultimate es más económico por ${surf_total - ultimate_total:.2f}.")
        else:
            st.info("Ambos planes tienen el mismo costo para este patrón de uso.")

# Información del creador y footer
st.markdown("""
---
<div style="text-align: center; padding: 1.5rem 0;">
    <p>Desarrollado por [Tu Nombre] | Portfolio Data Science</p>
    <p>Análisis basado en datos de la compañía de telefonía Megaline</p>
</div>
""", unsafe_allow_html=True)

# Ejecutar la aplicación localmente con: streamlit run app.py