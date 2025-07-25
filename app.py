import streamlit as st
import plotly.graph_objects as go
from prophet import Prophet
import pandas as pd
from datetime import date, timedelta, datetime

# --- SEU CÓDIGO crypto_utils.py (ou as funções implementadas aqui) ---
# Mantenha suas implementações reais para get_price, get_historical_data, get_all_symbols
# Se você estiver usando as funções de exemplo, garanta que elas gerem dados suficientes
from crypto_utils import get_price, get_historical_data, get_all_symbols
# --- FIM DO SEU CÓDIGO crypto_utils.py ---


# Configuração da página
st.set_page_config(page_title="Previsão Cripto", layout="wide")

# Título
st.title("📈 Previsão de Criptomoedas By: Israel Rodrigues")
st.markdown("Com *confiabilidade* de previsão e cotação em tempo real.")

# --- Sidebar - Configurações ---
st.sidebar.header("⚙️ Configurações de Previsão")

moedas = get_all_symbols()
symbol = st.sidebar.selectbox("Escolha a Cripto", moedas, key="select_crypto")

prediction_mode = st.sidebar.radio(
    "Modo de Previsão",
    ("Por Dias", "Por Data Específica"),
    key="prediction_mode"
)

forecast_period = None
if prediction_mode == "Por Dias":
    dias = st.sidebar.slider("Dias de Previsão", 1, 365 * 10, 30, key="forecast_days_slider")
    forecast_period = dias
else:
    min_date = date.today() + timedelta(days=1)
    max_date = date(2035, 12, 31)

    end_date = st.sidebar.date_input(
        "Prever até",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
        key="forecast_end_date"
    )
    forecast_period = (end_date - date.today()).days

if forecast_period is not None and forecast_period < 1:
    forecast_period = 1
    st.sidebar.warning("A data de previsão deve ser no futuro. Ajustado para 1 dia.")

# --- Exibe preço atual ---
st.subheader(f"💵 Cotação Atual: {symbol}")
preco_atual = get_price(symbol)
if preco_atual:
    st.markdown(f"### *${preco_atual:,.2f}*")
    st.markdown("(Dados em tempo real, sujeitos a pequenas variações)")
else:
    st.error("Não foi possível obter o preço atual. Verifique sua conexão ou a disponibilidade dos dados.")

# --- Obtém histórico ---
st.subheader(f"📊 Histórico de Preços: {symbol}")

# Tente obter mais dados históricos, o que pode ajudar em previsões de longo prazo
# e também a ter dados suficientes mesmo após a remoção de nulos.
historico = get_historical_data(symbol, days=365*3) # Tentar 3 anos de dados

# Ajusta formato para Prophet
# Verifique se 'ds' e 'y' existem antes de prosseguir
if 'ds' not in historico.columns or 'y' not in historico.columns:
    st.error(f"Os dados históricos para *{symbol}* não contêm as colunas 'ds' (data) e/ou 'y' (preço). Verifique a função get_historical_data.")
    st.stop()

# Remove linhas com valores nulos
historico = historico.dropna(subset=['ds', 'y'])

# Garante que 'ds' é datetime e 'y' é numérico
try:
    historico['ds'] = pd.to_datetime(historico['ds'])
    historico['y'] = pd.to_numeric(historico['y'])
except Exception as e:
    st.error(f"Erro ao converter colunas 'ds' ou 'y' para o formato correto: {e}. Verifique os dados brutos de get_historical_data.")
    st.stop()

# --- VERIFICAÇÃO CRÍTICA DE DADOS ANTES DO PROPHET ---
# Adicionei uma verificação mais robusta aqui
if historico.empty or len(historico) < 2:
    st.warning(f"🚨 *Dados insuficientes para gerar a previsão para {symbol}.*")
    st.info("O modelo de previsão requer pelo menos *dois pontos de dados históricos válidos* para funcionar. Por favor:")
    st.markdown("- *Tente selecionar outra criptomoeda.*")
    st.markdown("- *Verifique a sua fonte de dados* (crypto_utils.py) para garantir que ela está retornando um histórico robusto para a moeda selecionada.")
    st.stop() # Interrompe a execução do Streamlit aqui se não houver dados suficientes

# Gráfico histórico
fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(x=historico['ds'], y=historico['y'],
                              mode='lines', name='Histórico de Preços',
                              line=dict(color='orange', width=2)))
fig_hist.update_layout(
    title=f"*Tendência Histórica de Preços - {symbol}*",
    xaxis_title="Data",
    yaxis_title="Preço (USD)",
    hovermode="x unified",
    template="plotly_white"
)
st.plotly_chart(fig_hist, use_container_width=True)

# Previsão com Prophet
st.subheader("🔮 Previsão de Preços para o Futuro")
if forecast_period is None:
    st.warning("Selecione um período de previsão na barra lateral.")
else:
    with st.spinner(f"Gerando previsão para os próximos {forecast_period} dias..."):
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.95
        )
        model.fit(historico) # AQUI ERA ONDE DAVA O ERRO, AGORA PROTEGIDO

    fig_forecast = go.Figure()

    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_upper'],
        mode='lines', line=dict(width=0),
        name='Limite Superior', showlegend=False
    ))
    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_lower'],
        mode='lines', line=dict(width=0),
        fill='tonexty', fillcolor='rgba(100, 149, 237, 0.2)',
        name='Faixa de Confiança (95%)'
    ))

    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        mode='lines', name='Previsão', line=dict(color='blue', width=3, dash='dot')
    ))

    fig_forecast.add_trace(go.Scatter(
        x=historico['ds'], y=historico['y'],
        mode='markers', name='Dados Históricos (Pontinhos Pretos)',
        marker=dict(color='black', size=4, opacity=0.8)
    ))

    fig_forecast.update_layout(
        title=f"*Previsão de Preços para {symbol}* (Próximos {forecast_period} dias)",
        xaxis_title="Data", yaxis_title="Preço (USD)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)', bordercolor='rgba(0,0,0,0.2)', borderwidth=1)
    )

    st.plotly_chart(fig_forecast, use_container_width=True)

    st.markdown("""
    ---
    *Entendendo a Previsão:*
    * *Linha Azul Pontilhada:* É a previsão de preço do modelo.
    * *Área Azul Claro:* Representa a *faixa de confiança* de 95%. Isso significa que, com base nos dados históricos, há 95% de chance de o preço real cair dentro dessa área. Quanto mais estreita a faixa, maior a "confiança" do modelo naquela previsão.
    * *Pontos Pretos:* São os dados históricos reais usados para treinar o modelo.
    """)

    st.subheader("📊 Detalhes da Previsão em Tabela")
    forecast_details = forecast[forecast['ds'] > historico['ds'].max()]
    st.dataframe(forecast_details[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(
        columns={
            'ds': 'Data',
            'yhat': 'Previsão (USD)',
            'yhat_lower': 'Limite Inferior (USD)',
            'yhat_upper': 'Limite Superior (USD)'
        }
    ).set_index('Data').round(2))
