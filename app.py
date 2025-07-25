import streamlit as st
import plotly.graph_objects as go
from prophet import Prophet
import pandas as pd
from datetime import date, timedelta, datetime # Importar datetime e timedelta

# Assumindo que crypto_utils.py existe e contém as funções necessárias
# get_price, get_historical_data, get_all_symbols
# Se você não tiver esse arquivo, precisará implementar essas funções ou usar uma API
# Exemplo básico de como seriam (substitua pela sua lógica real):
# def get_price(symbol):
#     # Implemente a lógica para obter o preço atual da criptomoeda
#     return 50000.00 # Exemplo

# def get_historical_data(symbol, days):
#     # Implemente a lógica para obter dados históricos (ds, y)
#     # Isso deve retornar um DataFrame com colunas 'ds' (data) e 'y' (preço)
#     # Para fins de demonstração, vou criar dados falsos
#     today = date.today()
#     dates = [today - timedelta(days=i) for i in range(days)]
#     prices = [10000 + i*10 + (i%5)*500 for i in range(days)] # Dados de exemplo
#     df = pd.DataFrame({'ds': dates, 'y': prices})
#     return df

# def get_all_symbols():
#     # Implemente a lógica para obter todos os símbolos de criptomoedas
#     return ["BTC", "ETH", "ADA", "XRP"] # Exemplo

# --- Seu código crypto_utils.py (ou as funções implementadas aqui) ---
# Se o seu crypto_utils já funciona, ignore os exemplos acima.
from crypto_utils import get_price, get_historical_data, get_all_symbols
# --- Fim do seu código crypto_utils.py ---


# Configuração da página
st.set_page_config(page_title="Previsão Cripto", layout="wide")

# Título
st.title("📈 Previsão de Criptomoedas com IA")
st.markdown("Com *confiabilidade* de previsão e cotação em tempo real.") # Adicionando um subtítulo

# --- Sidebar - Configurações ---
st.sidebar.header("⚙️ Configurações de Previsão")

moedas = get_all_symbols()
symbol = st.sidebar.selectbox("Escolha a Cripto", moedas, key="select_crypto")

# Opção para escolher entre dias de previsão ou data final
prediction_mode = st.sidebar.radio(
    "Modo de Previsão",
    ("Por Dias", "Por Data Específica"),
    key="prediction_mode"
)

forecast_period = None
if prediction_mode == "Por Dias":
    dias = st.sidebar.slider("Dias de Previsão", 1, 365 * 10, 30, key="forecast_days_slider") # Estendido para 10 anos
    forecast_period = dias
else:
    # Definindo um limite máximo razoável, como 2035 ou 2040
    # A data inicial para o calendário será o dia atual + 1 dia
    min_date = date.today() + timedelta(days=1)
    max_date = date(2035, 12, 31) # Por exemplo, até o final de 2035

    end_date = st.sidebar.date_input(
        "Prever até",
        min_value=min_date,
        max_value=max_date,
        value=min_date, # Valor inicial para evitar erro se a data minima for maior que o default
        key="forecast_end_date"
    )
    # Calcular o número de dias a partir da data atual até a data final selecionada
    forecast_period = (end_date - date.today()).days

# Garantir que forecast_period seja pelo menos 1
if forecast_period is not None and forecast_period < 1:
    forecast_period = 1
    st.sidebar.warning("A data de previsão deve ser no futuro. Ajustado para 1 dia.")

# --- Exibe preço atual ---
st.subheader(f"💵 Cotação Atual: {symbol}")
preco_atual = get_price(symbol)
if preco_atual:
    st.markdown(f"### *${preco_atual:,.2f}*") # Destaque o preço atual
    st.markdown("(Dados em tempo real, sujeitos a pequenas variações)")
else:
    st.error("Não foi possível obter o preço atual. Verifique sua conexão ou a disponibilidade dos dados.")

# --- Obtém histórico ---
st.subheader(f"📊 Histórico de Preços: {symbol}")
historico = get_historical_data(symbol, days=365*2) # Obter mais dados históricos para melhor previsão

# Ajusta formato para Prophet
historico = historico.dropna()
historico['ds'] = pd.to_datetime(historico['ds'])
historico['y'] = historico['y'].astype(float)

# Verificação de dados
if historico.empty or len(historico) < 2:
    st.warning(f"Não há dados históricos suficientes para *{symbol}*. Por favor, tente outra moeda ou aguarde a disponibilidade dos dados.")
    st.stop()

# --- Gráfico histórico ---
fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(x=historico['ds'], y=historico['y'],
                              mode='lines', name='Histórico de Preços',
                              line=dict(color='orange', width=2)))
fig_hist.update_layout(
    title=f"*Tendência Histórica de Preços - {symbol}*",
    xaxis_title="Data",
    yaxis_title="Preço (USD)",
    hovermode="x unified",
    template="plotly_white" # Um tema mais limpo
)
st.plotly_chart(fig_hist, use_container_width=True)

# --- Previsão com Prophet ---
st.subheader("🔮 Previsão de Preços para o Futuro")
if forecast_period is None:
    st.warning("Selecione um período de previsão na barra lateral.")
else:
    with st.spinner(f"Gerando previsão para os próximos {forecast_period} dias..."):
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True, # Adicionado para melhor sazonalidade
            yearly_seasonality=True, # Adicionado para melhor sazonalidade anual
            interval_width=0.95 # Aumenta a largura do intervalo de confiança para 95%
        )
        model.fit(historico)
        future = model.make_future_dataframe(periods=forecast_period)
        forecast = model.predict(future)

    # --- Gráfico de Previsão com "Pontinhos Pretos" e Faixa de Confiança ---
    fig_forecast = go.Figure()

    # Faixa de Confiança (Sua "Marca de Confiança")
    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_upper'],
        mode='lines', line=dict(width=0),
        name='Limite Superior', showlegend=False
    ))
    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_lower'],
        mode='lines', line=dict(width=0),
        fill='tonexty', fillcolor='rgba(100, 149, 237, 0.2)', # Tom de azul mais suave
        name='Faixa de Confiança (95%)' # Nomeando para clareza
    ))

    # Linha de Previsão
    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        mode='lines', name='Previsão', line=dict(color='blue', width=3, dash='dot') # Linha de previsão destacada
    ))

    # Histórico (Os "Pontinhos Pretos")
    fig_forecast.add_trace(go.Scatter(
        x=historico['ds'], y=historico['y'],
        mode='markers', name='Dados Históricos (Pontinhos Pretos)',
        marker=dict(color='black', size=4, opacity=0.8) # Tamanho um pouco menor para o ponto preto
    ))

    fig_forecast.update_layout(
        title=f"*Previsão de Preços para {symbol}* (Próximos {forecast_period} dias)",
        xaxis_title="Data", yaxis_title="Preço (USD)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)', bordercolor='rgba(0,0,0,0.2)', borderwidth=1)
    )

    st.plotly_chart(fig_forecast, use_container_width=True)
