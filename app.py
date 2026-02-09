import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    layout="wide",
    page_title="Data Salary Insights Pro",
    page_icon="📊"
)

# 2. Carregamento de Dados com Cache
@st.cache_data
def load_data():
    # Lendo o arquivo local conforme sua estrutura atual
    data = pd.read_csv("dados-imersao_final.csv")
    # Padronização estética dos cargos
    data['cargo'] = data['cargo'].str.title()
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar o arquivo: {e}")
    st.stop()

# --- Estilização CSS para métricas ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- Barra Lateral (Filtros) ---
with st.sidebar:
    st.title("⚙️ Filtros")
    
    with st.expander("📅 Período e Contrato", expanded=True):
        anos = st.multiselect("Anos", sorted(df['ano'].unique()), default=df['ano'].unique())
        contratos = st.multiselect("Tipos de Contrato", sorted(df['contrato'].unique()), default=df['contrato'].unique())
    
    with st.expander("👤 Perfil Profissional", expanded=True):
        senioridades = st.multiselect("Senioridade", sorted(df['senioridade'].unique()), default=df['senioridade'].unique())
        tamanhos = st.multiselect("Tamanho da Empresa", sorted(df['tamanho_empresa'].unique()), default=df['tamanho_empresa'].unique())

# --- Processamento da Filtragem ---
df_filtrado = df[
    (df['ano'].isin(anos)) &
    (df['senioridade'].isin(senioridades)) &
    (df['contrato'].isin(contratos)) &
    (df['tamanho_empresa'].isin(tamanhos))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore tendências salariais globais. Use os filtros à esquerda para refinar sua análise.")

# Verificação se o DataFrame contém dados após o filtro
if not df_filtrado.empty:
    # --- Métricas Principais (KPIs) ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Salário Médio", f"US$ {df_filtrado['usd'].mean():,.0f}")
    m2.metric("Salário Máximo", f"US$ {df_filtrado['usd'].max():,.0f}")
    m3.metric("Total de Registros", f"{len(df_filtrado):,}")
    m4.metric("Cargo Mais Comum", df_filtrado['cargo'].mode()[0])

    st.markdown("---")

    # --- Organização em Abas ---
    tab1, tab2, tab3 = st.tabs(["📊 Distribuição e Proporções", "🌍 Mapa Global", "📋 Tabela de Dados"])

    with tab1:
        # Primeira Linha de Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Top Cargos (Barras)
            top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
            grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
            )
            grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(grafico_cargos, use_container_width=True)

        with col2:
            grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
            )
            grafico_hist.update_layout(title_x=0.1)
            st.plotly_chart(grafico_hist, use_container_width=True)

        # Segunda Linha de Gráficos
        col3, col4 = st.columns(2)

        with col3:
            # 3. Gráfico de Pizza (Donut) - Tipos de Trabalho
            remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
            remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
            fig_pie = px.pie(
                remoto_contagem, names='tipo_trabalho', values='quantidade',
                title='Proporção de Modalidade de Trabalho',
                hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col4:
            # 2. Boxplot de Senioridade (Destaque Pro)
            fig_box = px.box(
                df_filtrado, x='senioridade', y='usd', color='senioridade',
                title="Dispersão Salarial por Senioridade",
                labels={'usd': 'Salário (USD)', 'senioridade': 'Nível'},
                category_orders={"senioridade": ["Junior", "Pleno", "Senior", "Especialista"]}
            )
            st.plotly_chart(fig_box, use_container_width=True)

    with tab2:
        st.subheader("Visão Geográfica")
        # Mapa para Cientistas de Dados (conforme solicitado no app.py)
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        
        if not df_ds.empty:
            media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
            fig_map = px.choropleth(
                media_ds_pais, locations='residencia_iso3', color='usd',
                color_continuous_scale='rdylgn',
                title='Salário Médio de Cientista de Dados por País',
                labels={'usd': 'Média (USD)', 'residencia_iso3': 'País'}
            )
            fig_map.update_layout(height=600)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Selecione o cargo 'Data Scientist' ou ajuste os filtros para visualizar o mapa.")

    with tab3:
        st.subheader("Explorador de Dados")
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar dados filtrados como CSV",
            data=csv,
            file_name='salarios_filtrados.csv',
            mime='text/csv',
        )
        st.dataframe(df_filtrado, use_container_width=True)

else:
    st.error("⚠️ Nenhum dado encontrado para os filtros selecionados. Por favor, ajuste as configurações na barra lateral.")