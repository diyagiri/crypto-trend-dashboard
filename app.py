# app.py
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px

from data import (
    fetch_coins_market,
    fetch_trending_coins,
    fetch_market_chart,
    fetch_global_metrics
)
from utils import format_percent, compute_rsi, compute_macd

# ── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(page_title="Real-Time Crypto Dashboard", layout="wide")

# ── Title & Description (Centered) ──────────────────────────────────────────
st.markdown(
    "<h1 style='text-align: center;'>📈 Real-Time Crypto Dashboard</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center;'>A live, interactive dashboard powered by CoinGecko, showcasing key market insights and technical indicators for portfolio analysis.</p>",
    unsafe_allow_html=True
)

# ── About this Dashboard ─────────────────────────────────────────────────────
with st.expander("ℹ️ About this Dashboard", expanded=False):
    st.write("""
        This dashboard demonstrates an end-to-end real-time analytics application:
        1. **Data Ingestion**: Fetch live market data from the free CoinGecko API.
        2. **Visualization**: Display global metrics, price charts, correlation heatmaps, and performance movers.
        3. **Technical Analysis**: Compute RSI and MACD indicators to highlight momentum shifts.
        4. **Portfolio Tracking**: Input hypothetical holdings to calculate P&L and allocation.

        Designed as a portfolio project it emphasizes code organization, interactivity, and clear explanations for beginner audiences.
    """)

# ── Auto-refresh every 60 seconds ───────────────────────────────────────────
st_autorefresh(interval=60_000, limit=None, key="refresh")

# ── Sidebar controls ─────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")
limit = st.sidebar.slider(
    "How many coins to fetch?", 10, 200, 100, 10,
    help="Fetch the top N coins by market capitalization."
)
threshold = st.sidebar.slider(
    "Alert threshold (% change)", 1.0, 50.0, 10.0, 1.0,
    help="24h % change beyond which coins appear in Movers & Rankings alerts."
)
rolling_window = st.sidebar.slider(
    "Rolling-average window", 1, 20, 5,
    help="Window size for the rolling-average price chart (currently unused)."
)
hist_days = st.sidebar.slider(
    "Historical days", 1, 365, 30, 1,
    help="Number of past days to fetch for historical charts and correlations."
)

# ── Data fetching ────────────────────────────────────────────────────────────
with st.spinner("Loading data…"):
    df = fetch_coins_market(per_page=limit)
    global_m = fetch_global_metrics()
    try:
        trending = fetch_trending_coins()
    except Exception:
        trending = None

st.markdown("---")

# ── Global market metrics ────────────────────────────────────────────────────
with st.expander("ℹ️ What are Global Market Metrics?"):
    st.write("""
        - **Total Market Cap**: Sum of all coins' market capitalization.
        - **24h Cap Δ**: Percentage change in total market cap over 24 hours.
        - **Active Cryptocurrencies**: Number of listed coins on CoinGecko.
        - **BTC Dominance**: Bitcoin's share of total market capitalization.
    """)
cols = st.columns(4)
cols[0].metric("🌐 Total Market Cap", f"${global_m['total_market_cap']:,}")
cols[1].metric("24h Cap Δ", f"{global_m['market_cap_change_pct_24h']:.2f}%")
cols[2].metric("🔢 Active Cryptocurrencies", global_m["active_cryptocurrencies"])
cols[3].metric("🐂 BTC Dominance", f"{global_m['btc_dominance']:.2f}%")

st.markdown("---")

# ── Top-coin key metrics with logo ────────────────────────────────────────────
top = df.iloc[0]
with st.expander("ℹ️ Top Coin Overview"):
    st.write("Displays the current leader in market cap, with its logo, market cap value, and 24h volume/change.")
c1, c2 = st.columns([1, 3])
with c1:
    st.image(top["image"], width=60)
with c2:
    st.metric("🏅 Top Market Cap", top["name"], f"${top['market_cap']:,}")
    st.metric("📊 24h Volume & Δ", f"${top['total_volume']:,}", f"{top['price_change_percentage_24h']:.2f}%")

st.markdown("---")

# Prepare map from symbol to id for historical fetch
symbol_to_id = dict(zip(df["symbol"], df["id"]))

# ── Main tabs ────────────────────────────────────────────────────────────────
tabs = st.tabs(["📈 Trends", "🔀 Compare Coins", "📊 Movers & Rankings", "💼 Portfolio"])

# Tab 0: Trends
with tabs[0]:
    st.header("24h % Change Distribution")
    with st.expander("ℹ️ About this chart"):
        st.write("Bar chart showing each coin’s percentage price change over the last 24 hours.")
    st.bar_chart(df.set_index("symbol")["price_change_percentage_24h"])

    st.subheader("Historical Price Chart")
    with st.expander("ℹ️ Historical Chart Info"):
        st.write("Select a coin to view its daily closing price over the past N days.")
    coin_choice = st.selectbox("Select coin for history:", df["id"].tolist())
    hist_df = fetch_market_chart(coin_choice, days=hist_days)
    st.line_chart(hist_df.set_index("timestamp")["price"])

    with st.expander("Technical Indicators"):
        st.write("Plots of RSI and MACD help identify momentum and trend shifts.")
        ti = compute_rsi(hist_df)
        ti = compute_macd(ti)
        st.subheader("RSI")
        st.line_chart(ti.set_index("timestamp")["rsi"])
        st.caption("RSI: over 70 = overbought; below 30 = oversold.")
        st.subheader("MACD")
        st.line_chart(ti.set_index("timestamp")[["macd", "macd_signal"]])
        st.caption("MACD: difference between fast & slow EMAs; signal is its EMA.")

    st.subheader("Trending Coins")
    if trending is not None and not trending.empty:
        st.table(trending)
    else:
        st.info("Trending data unavailable.")

# Tab 1: Compare Coins
with tabs[1]:
    st.header("Compare Historical Prices & Correlation")
    with st.expander("ℹ️ How to use this section"):
        st.write("Select coins by symbol to compare price trends and compute daily returns correlation.")
    selected = st.multiselect("Pick coins (symbol):", df["symbol"].tolist(), default=df["symbol"][:3].tolist())
    if selected:
        cols = st.columns(len(selected))
        for i, sym in enumerate(selected):
            row = df[df["symbol"] == sym].iloc[0]
            cols[i].image(row["image"], width=50)
            cols[i].metric(sym, f"${row['current_price']:,}")

        # Historical price and returns
        price_hist = pd.DataFrame()
        for sym in selected:
            coin_id = symbol_to_id[sym]
            h = fetch_market_chart(coin_id, days=hist_days).set_index("timestamp")["price"]
            price_hist[sym] = h
        st.subheader("Historical Price Over Time")
        st.line_chart(price_hist)

        returns = price_hist.pct_change(fill_method=None).dropna()
        st.subheader("Returns Correlation (Daily % Change)")
        fig = px.imshow(returns.corr(), text_auto=True, aspect="auto")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one coin.")

# Tab 2: Movers & Rankings
with tabs[2]:
    st.header("🚀 Movers & 🏆 Rankings")
    with st.expander("ℹ️ Explanation"):
        st.write("""
            - **Top Movers**: Coins with the highest gains (gainers) and losses (losers) by 24h % change.
            - **Alerts**: Any coin whose 24h % change exceeds your alert threshold.
            - **Top 10**: The largest networks ranked by market capitalization.
        """)
    movers_cols = st.columns(2)
    gainers = df.nlargest(5, "price_change_percentage_24h")[["symbol", "price_change_percentage_24h", "image"]]
    losers = df.nsmallest(5, "price_change_percentage_24h")[["symbol", "price_change_percentage_24h", "image"]]
    with movers_cols[0]:
        st.markdown("**Gainers**")
        for _, r in gainers.iterrows():
            rc1, rc2 = st.columns([1, 3])
            rc1.image(r["image"], width=30)
            rc2.write(f"**{r['symbol']}**: +{r['price_change_percentage_24h']:.2f}%")
    with movers_cols[1]:
        st.markdown("**Losers**")
        for _, r in losers.iterrows():
            rc1, rc2 = st.columns([1, 3])
            rc1.image(r["image"], width=30)
            rc2.write(f"**{r['symbol']}**: {r['price_change_percentage_24h']:.2f}%")

    alerts = df[abs(df["price_change_percentage_24h"]) > threshold]
    if not alerts.empty:
        st.warning(f"⚠️ Moves > {threshold}%")
        st.table(alerts[["symbol", "price_change_percentage_24h"]].rename(columns={"price_change_percentage_24h": "% Change"}))

    st.markdown("---")
    st.subheader("Top 10 by Market Cap")
    top10_df = df.nlargest(10, "market_cap")[["symbol", "market_cap", "image"]].reset_index(drop=True)
    cols = st.columns(10)
    for i, r in top10_df.iterrows():
        cols[i].image(r["image"], width=40)
        cols[i].caption(r["symbol"])
    st.bar_chart(top10_df.set_index("symbol")["market_cap"])

# Tab 3: Portfolio
with tabs[3]:
    st.header("💼 Portfolio Tracker")
    with st.expander("ℹ️ How to track your portfolio"):
        st.write("Enter how many units you hold and your purchase price to calculate current value and P&L.")
    selected = st.multiselect("Select coins to track:", df["symbol"].tolist())
    holdings = []
    for sym in selected:
        qty = st.number_input(f"{sym} quantity", 0.0, 1e6, 0.0, key=f"{sym}_qty")
        pp = st.number_input(f"{sym} purchase price (USD)", 0.0, 1e6, 0.0, key=f"{sym}_pp")
        if qty and pp:
            cp = float(df[df["symbol"] == sym]["current_price"].iloc[0])
            holdings.append({
                "symbol": sym,
                "quantity": qty,
                "purchase_price": pp,
                "current_price": cp
            })
    if holdings:
        port_df = pd.DataFrame(holdings).set_index("symbol")
        port_df["current_value"] = port_df["quantity"] * port_df["current_price"]
        port_df["cost_basis"] = port_df["quantity"] * port_df["purchase_price"]
        port_df["pnl_pct"] = (port_df["current_value"] - port_df["cost_basis"]) / port_df["cost_basis"] * 100
        st.metric("Total Portfolio Value", f"${port_df['current_value'].sum():,.2f}")
        st.table(port_df[["quantity", "purchase_price", "current_price", "current_value", "pnl_pct"]])
        fig_pie = px.pie(port_df, values="current_value", names=port_df.index, title="Allocation")
        st.plotly_chart(fig_pie, use_container_width=True)
