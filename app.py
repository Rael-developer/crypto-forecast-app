import streamlit as st
import plotly.graph_objects as go
from prophet import Prophet
from crypto_utils import get_price, get_historical_data, get_all_symbols
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Previsão Cripto", layout="wide")

# Título
st.title("📈 Previsão de Criptomoedas com IA")

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações")
moedas = get_all_symbols()
symbol = st.sidebar.selectbox("Escolha a Cripto", moedas, key="select_crypto")
dias = st.sidebar.slider("Dias de Previsão", 1, 60, 30, key="forecast_days")

# Exibe preço atual
st.subheader(f"Preço Atual de {symbol}")
preco_atual = get_price(symbol)
if preco_atual:
    st.metric(label="Preço Atual", value=f"${preco_atual:,.2f}")
else:
    st.error("Não foi possível obter o preço atual.")

# Obtém histórico
st.subheader(f"Histórico de {symbol}")
historico = get_historical_data(symbol, days=365)

# Verificação de dados
if historico.empty or len(historico) < 2:
    st.warning(f"Sem dados suficientes para {symbol}. Tente outra moeda.")
    st.stop()

# Gráfico histórico
fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(x=historico['ds'], y=historico['y'],
                              mode='lines', name='Histórico', line=dict(color='orange')))
fig_hist.update_layout(title=f"Histórico de Preços - {symbol}", xaxis_title="Data", yaxis_title="Preço (USD)")
st.plotly_chart(fig_hist, use_container_width=True)

# Previsão com Prophet
st.subheader("🔮 Previsão para os próximos dias")
with st.spinner("Treinando modelo Prophet para previsão..."):
    model = Prophet(daily_seasonality=True)
    model.fit(historico)
    future = model.make_future_dataframe(periods=dias)
    forecast = model.predict(future)

# Gráfico previsão
fig_forecast = go.Figure()
fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines',
                                  name='Previsão', line=dict(color='blue')))
fig_forecast.add_trace(go.Scatter(x=historico['ds'], y=historico['y'], mode='markers',
                                  name='Histórico', marker=dict(color='black', size=5)))
fig_forecast.update_layout(title=f"Previsão de {symbol} para {dias} dias", xaxis_title="Data", yaxis_title="Preço (USD)")
st.plotly_chart(fig_forecast, use_container_width=True)

# Detalhes do forecast
st.subheader("📊 Detalhes da Previsão")
st.dataframe(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(dias))
