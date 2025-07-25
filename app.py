import streamlit as st
import pandas as pd
from binance_utils import get_price, get_historical_data, get_all_symbols
from forecast_utils import treinar_previsao
from telegram_bot import send_telegram
from plotly import graph_objects as go

st.set_page_config(page_title="Previsão Cripto", layout="wide", page_icon="📈")

st.title("📊 Previsão de Criptomoedas")
st.markdown("### Previsões usando Binance + Prophet + Alertas do Telegram")

st.sidebar.header("Configurações")
symbol = st.sidebar.selectbox("Escolha a Cripto", get_all_symbols())
dias = st.sidebar.slider("Dias de previsão", 1, 60, 30)
alerta = st.sidebar.checkbox("Enviar alerta no Telegram", value=False)

with st.spinner("🔍 Obtendo preço atual..."):
   preco_atual = get_price(symbol)
if preco_atual is None:
    st.error(f"Não foi possível obter o preço de {symbol}. Verifique a API ou tente outra moeda.")
else:
    st.metric(label=f"Preço atual de {symbol}", value=f"${preco_atual:.2f}")

st.subheader("📈 Histórico e Previsão")
with st.spinner("📥 Baixando dados históricos da Binance..."):
   historico = get_historical_data(symbol)
if historico.empty:
    st.warning(f"Sem dados históricos para {symbol}. Tente outra moeda.")
else:
    # Mostra gráfico e previsão

with st.spinner("🔮 Treinando modelo Prophet para previsão... (pode levar alguns segundos)"):
    forecast = treinar_previsao(historico, dias)

fig = go.Figure()
fig.add_trace(go.Scatter(x=historico['ds'], y=historico['y'], mode='markers',
                         name='Histórico', marker=dict(color='black', size=5)))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines',
                         name='Previsão', line=dict(color='blue', width=2)))
fig.add_trace(go.Scatter(
    x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
    y=pd.concat([forecast['yhat_upper'], forecast['yhat_lower'][::-1]]),
    fill='toself', fillcolor='rgba(0,123,255,0.2)',
    line=dict(color='rgba(255,255,255,0)'), hoverinfo="skip",
    showlegend=True, name='Intervalo'
))
fig.update_layout(template="plotly_dark", hovermode="x unified",
                  title=f"Previsão para {symbol}", xaxis_title="Data", yaxis_title="Preço (USDT)")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 Dados previstos")
st.write(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(dias))

if alerta:
    with st.spinner("📤 Enviando alerta para Telegram..."):
        send_telegram(f"Preço atual de {symbol}: ${preco_atual:.2f}")
    st.success("✅ Alerta enviado para o Telegram!")
