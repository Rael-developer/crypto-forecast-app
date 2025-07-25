import requests
import streamlit as st

TOKEN = st.secrets["TOKEN"]
CHAT_ID = st.secrets["CHAT_ID"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)
