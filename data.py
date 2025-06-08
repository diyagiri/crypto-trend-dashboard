# data.py
import requests
import pandas as pd
import streamlit as st
from datetime import datetime

BASE_URL = "https://api.coingecko.com/api/v3"

@st.cache_data(ttl=60)
def fetch_coins_market(vs_currency="usd", per_page=100, page=1) -> pd.DataFrame:
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": False,
        "price_change_percentage": "24h",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    df["timestamp"] = pd.to_datetime(datetime.utcnow())
    return df

@st.cache_data(ttl=300)
def fetch_trending_coins() -> pd.DataFrame:
    url = f"{BASE_URL}/search/trending"
    resp = requests.get(url)
    resp.raise_for_status()
    items = resp.json().get("coins", [])
    df = pd.DataFrame([c["item"] for c in items])
    return df[["id", "name", "symbol", "market_cap_rank", "score"]]

@st.cache_data(ttl=300)
def fetch_market_chart(coin_id: str, vs_currency="usd", days=30) -> pd.DataFrame:
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days, "interval": "daily"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame({
        "timestamp": [datetime.utcfromtimestamp(ts // 1000) for ts, _ in data["prices"]],
        "price": [p for _, p in data["prices"]],
        "market_cap": [m for _, m in data["market_caps"]],
        "total_volume": [v for _, v in data["total_volumes"]],
    })
    return df

@st.cache_data(ttl=300)
def fetch_global_metrics() -> dict:
    url = f"{BASE_URL}/global"
    resp = requests.get(url)
    resp.raise_for_status()
    d = resp.json().get("data", {})
    return {
        "total_market_cap": d.get("total_market_cap", {}).get("usd", 0),
        "market_cap_change_pct_24h": d.get("market_cap_change_percentage_24h_usd", 0),
        "active_cryptocurrencies": d.get("active_cryptocurrencies", 0),
        "markets": d.get("markets", 0),
        "btc_dominance": d.get("market_cap_percentage", {}).get("btc", 0),
    }
