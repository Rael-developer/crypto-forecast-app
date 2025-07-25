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
st.title("📈 Previsão de Criptomoedas com IA")
st.markdown("Com *confiabilidade* de previsão e cotação em tempo real.")

# --- Sidebar - Configura…
[00:31, 25/07/2025] Mr. Robot: import streamlit as st
import yfinance as yf
from pycoingecko import CoinGeckoAPI
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta

# --- Configurações Iniciais ---
st.set_page_config(page_title="Mercado Financeiro", layout="wide", icon="💰")

# --- Instâncias de APIs/Bibliotecas ---
cg = CoinGeckoAPI()

# --- Funções de Busca de Dados ---

@st.cache_data(ttl=3600) # Cache para 1 hora
def get_stock_info(ticker_symbol):
    """Busca informações de ações/FIIs usando yfinance."""
    ticker = yf.Ticker(ticker_symbol)
    try:
        info = ticker.info
        hist = ticker.history(period="1y") # 1 ano de histórico
        dividends = ticker.dividends
        return info, hist, dividends
    except Exception as e:
        st.error(f"Erro ao buscar dados para {ticker_symbol}: {e}")
        return None, None, None

@st.cache_data(ttl=300) # Cache para 5 minutos
def get_crypto_price(crypto_id):
    """Busca o preço atual de criptomoeda usando CoinGecko."""
    try:
        price_data = cg.get_price(ids=crypto_id, vs_currencies='usd')
        return price_data[crypto_id]['usd'] if crypto_data else None
    except Exception as e:
        st.error(f"Erro ao buscar preço de {crypto_id}: {e}")
        return None

@st.cache_data(ttl=3600)
def get_top_cryptos(count=100):
    """Busca as top N criptos por market cap para seleção."""
    try:
        # Pega as top criptos por market cap, incluindo o ID (para get_price)
        coins = cg.get_coins_markets(vs_currency='usd', per_page=count, page=1)
        # Retorna um dicionário {nome: id} para o selectbox
        return {coin['name']: coin['id'] for coin in coins}
    except Exception as e:
        st.error(f"Erro ao buscar lista de criptomoedas: {e}")
        return {}


# --- Título Principal ---
st.title("💸 Visão Geral do Mercado Financeiro")
st.markdown("Cotações, Históricos e Projeções para Ações, FIIs e Criptomoedas.")

# --- SIDEBAR: Seleção de Ativos ---
st.sidebar.title("🔍 Selecione um Ativo")

# --- Opção de escolha (Rádio Button) ---
asset_type = st.sidebar.radio(
    "Escolha o tipo de Ativo:",
    ("Ações", "Fundos Imobiliários (FIIs)", "Criptomoedas"),
    key="asset_type_selection"
)

# --- Seção de Ações ---
if asset_type == "Ações":
    st.sidebar.header("📈 Ações")
    # Exemplos de tickers de ações brasileiras (você pode expandir)
    stock_tickers = {
        "Petrobras (PETR4)": "PETR4.SA",
        "Vale (VALE3)": "VALE3.SA",
        "Itaú (ITUB4)": "ITUB4.SA",
        "Banco do Brasil (BBAS3)": "BBAS3.SA",
        "Ambev (ABEV3)": "ABEV3.SA",
        "WEG (WEGE3)": "WEGE3.SA",
        "Magazine Luiza (MGLU3)": "MGLU3.SA",
        "Gerdau (GGBR4)": "GGBR4.SA",
    }
    selected_stock_name = st.sidebar.selectbox("Escolha uma Ação:", list(stock_tickers.keys()))
    selected_ticker = stock_tickers[selected_stock_name]

    st.header(f"📈 Cotação e Análise: {selected_stock_name}")

    info, hist_data, dividends = get_stock_info(selected_ticker)

    if info and not hist_data.empty:
        # Cotação Atual
        current_price = info.get('regularMarketPrice')
        if current_price:
            st.metric(label=f"Preço Atual ({selected_ticker})", value=f"R$ {current_price:,.2f}")
        else:
            st.warning("Não foi possível obter o preço atual.")

        st.subheader("Histórico de Preços (Último Ano)")
        fig = go.Figure(data=[go.Candlestick(x=hist_data.index,
                                             open=hist_data['Open'],
                                             high=hist_data['High'],
                                             low=hist_data['Low'],
                                             close=hist_data['Close'])])
        fig.update_layout(xaxis_rangeslider_visible=False, title=f"Gráfico de Candlestick de {selected_stock_name}",
                          xaxis_title="Data", yaxis_title="Preço (R$)")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Histórico de Dividendos/JCP")
        if not dividends.empty:
            st.dataframe(dividends.reset_index().rename(columns={'Date': 'Data', 'Dividends': 'Valor (R$)'}))
        else:
            st.info("Nenhum registro de dividendos/JCP encontrado para este ativo no último ano.")

        # --- Seção de Projeção (Placeholder) ---
        st.subheader("🔮 Projeção (Subir/Cair) - Em Desenvolvimento")
        st.info("A funcionalidade de projeção para ações será implementada aqui. "
                "Poderemos analisar tendências e indicadores para sugerir uma direção futura.")
        # Exemplo básico de uma "projeção" usando a última variação
        if 'Close' in hist_data.columns and len(hist_data) > 1:
            latest_close = hist_data['Close'].iloc[-1]
            previous_close = hist_data['Close'].iloc[-2]
            change = ((latest_close - previous_close) / previous_close) * 100
            if change > 0:
                st.markdown(f"*Tendência Recente (1 dia):* ⬆️ Subiu *{change:.2f}%*. Indicador inicial positivo.")
            elif change < 0:
                st.markdown(f"*Tendência Recente (1 dia):* ⬇️ Caiu *{abs(change):.2f}%*. Indicador inicial negativo.")
            else:
                st.markdown("*Tendência Recente (1 dia):* Sem alteração significativa.")
        else:
            st.markdown("Dados insuficientes para análise de tendência recente.")


# --- Seção de Fundos Imobiliários (FIIs) ---
elif asset_type == "Fundos Imobiliários (FIIs)":
    st.sidebar.header("🏠 Fundos Imobiliários (FIIs)")
    # Exemplos de tickers de FIIs brasileiros (você pode expandir)
    fii_tickers = {
        "MXRF11": "MXRF11.SA",
        "HGLG11": "HGLG11.SA",
        "XPML11": "XPML11.SA",
        "KNCR11": "KNCR11.SA",
        "CPTS11": "CPTS11.SA",
    }
    selected_fii_name = st.sidebar.selectbox("Escolha um FII:", list(fii_tickers.keys()))
    selected_ticker = fii_tickers[selected_fii_name]

    st.header(f"🏠 Cotação e Análise: {selected_fii_name}")

    info, hist_data, dividends = get_stock_info(selected_ticker) # Usa a mesma função para FIIs

    if info and not hist_data.empty:
        # Cotação Atual
        current_price = info.get('regularMarketPrice')
        if current_price:
            st.metric(label=f"Preço Atual ({selected_ticker})", value=f"R$ {current_price:,.2f}")
        else:
            st.warning("Não foi possível obter o preço atual.")

        st.subheader("Histórico de Preços (Último Ano)")
        fig = go.Figure(data=[go.Candlestick(x=hist_data.index,
                                             open=hist_data['Open'],
                                             high=hist_data['High'],
                                             low=hist_data['Low'],
                                             close=hist_data['Close'])])
        fig.update_layout(xaxis_rangeslider_visible=False, title=f"Gráfico de Candlestick de {selected_fii_name}",
                          xaxis_title="Data", yaxis_title="Preço (R$)")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Histórico de Rendimentos/Dividendos")
        if not dividends.empty:
            st.dataframe(dividends.reset_index().rename(columns={'Date': 'Data', 'Dividends': 'Valor (R$)'}))
        else:
            st.info("Nenhum registro de rendimentos/dividendos encontrado para este FII no último ano.")

        # --- Seção de Projeção (Placeholder) ---
        st.subheader("🔮 Projeção (Subir/Cair) - Em Desenvolvimento")
        st.info("A funcionalidade de projeção para FIIs será implementada aqui. "
                "Poderemos analisar tendências e indicadores para sugerir uma direção futura.")
        # Exemplo básico de uma "projeção" usando a última variação
        if 'Close' in hist_data.columns and len(hist_data) > 1:
            latest_close = hist_data['Close'].iloc[-1]
            previous_close = hist_data['Close'].iloc[-2]
            change = ((latest_close - previous_close) / previous_close) * 100
            if change > 0:
                st.markdown(f"*Tendência Recente (1 dia):* ⬆️ Subiu *{change:.2f}%*. Indicador inicial positivo.")
            elif change < 0:
                st.markdown(f"*Tendência Recente (1 dia):* ⬇️ Caiu *{abs(change):.2f}%*. Indicador inicial negativo.")
            else:
                st.markdown("*Tendência Recente (1 dia):* Sem alteração significativa.")
        else:
            st.markdown("Dados insuficientes para análise de tendência recente.")

# --- Seção de Criptomoedas ---
else: # asset_type == "Criptomoedas"
    st.sidebar.header("💎 Criptomoedas")
    # Tenta buscar as 100 maiores criptos por market cap.
    # Pode demorar um pouco na primeira execução devido à API.
    crypto_symbols_map = get_top_cryptos()
    if crypto_symbols_map:
        selected_crypto_name = st.sidebar.selectbox(
            "Escolha uma Criptomoeda:",
            list(crypto_symbols_map.keys()),
            key="select_crypto_sidebar"
        )
        selected_crypto_id = crypto_symbols_map[selected_crypto_name]

        st.header(f"💎 Cotação: {selected_crypto_name}")
        with st.spinner(f"Buscando cotação para {selected_crypto_name}..."):
            crypto_price = get_crypto_price(selected_crypto_id)

        if crypto_price:
            st.metric(label=f"Preço Atual (USD)", value=f"${crypto_price:,.2f}")
            st.info("Para criptomoedas, exibimos apenas a cotação atual. Não há projeção ou histórico de dividendos.")
        else:
            st.warning(f"Não foi possível obter a cotação para {selected_crypto_name}. Tente novamente mais tarde.")
    else:
        st.warning("Não foi possível carregar a lista de criptomoedas. Tente recarregar a página.")

st.sidebar.markdown("---")
st.sidebar.info("Dados fornecidos por Yahoo Finance e CoinGecko.")
