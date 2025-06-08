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
st.title("📈 Real-Time Crypto Dashboard")
st.markdown("A live, interactive dashboard powered by CoinGecko")

# ── Auto-refresh every 60 seconds ───────────────────────────────────────────
st_autorefresh(interval=60_000, limit=None, key="refresh")

# ── Sidebar controls ─────────────────────────────────────────────────────────
limit = st.sidebar.slider(
    "How many coins to fetch?",
    min_value=10,
    max_value=200,
    value=100,
    step=10,
    help="Pick the top N coins by market cap (descending)."
)
threshold = st.sidebar.slider(
    "Alert threshold (% change)",
    min_value=1.0,
    max_value=50.0,
    value=10.0,
    step=1.0,
    help="Coins moving more than this % in 24h will display alerts."
)
rolling_window = st.sidebar.slider(
    "Rolling-average window",
    min_value=1,
    max_value=20,
    value=5,
    help="Window size for the rolling-average price chart."
)
hist_days = st.sidebar.slider(
    "Historical days",
    min_value=1,
    max_value=365,
    value=30,
    step=1,
    help="Number of past days to show in the historical price chart."
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
gm1, gm2, gm3, gm4 = st.columns(4)
gm1.metric("🌐 Total Market Cap", f"${global_m['total_market_cap']:,}")
gm2.metric("24h Cap Δ", f"{global_m['market_cap_change_pct_24h']:.2f}%")
gm3.metric("🔢 Active Cryptocurrencies", global_m["active_cryptocurrencies"])
gm4.metric("🐂 BTC Dominance", f"{global_m['btc_dominance']:.2f}%")

st.markdown("---")

# ── Top-coin key metrics with logo ────────────────────────────────────────────
top = df.iloc[0]
c1, c2 = st.columns([1, 3])
with c1:
    st.image(top["image"], width=60)
with c2:
    st.metric("🏅 Top Market Cap", top["name"], f"${top['market_cap']:,}")
    st.metric("📊 24h Volume & Δ", f"${top['total_volume']:,}", f"{top['price_change_percentage_24h']:.2f}%")

st.markdown("---")

# ── Main tabs ────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📈 Trends",
    "🔀 Compare Coins",
    "📊 Movers & Rankings",
    "💼 Portfolio"
])

# Tab 0: Trends
with tabs[0]:
    st.header("24h % Change Distribution")
    st.bar_chart(df.set_index("symbol")["price_change_percentage_24h"])

    st.subheader("Historical Price Chart")
    coin_choice = st.selectbox(
        "Select coin for history:",
        options=df["id"].tolist(),
        index=0,
        help="Pick one coin to view its historical price and technical indicators."
    )
    hist_df = fetch_market_chart(coin_choice, days=hist_days)
    st.line_chart(hist_df.set_index("timestamp")["price"])

    with st.expander("Technical Indicators"):
        ti = compute_rsi(hist_df)
        ti = compute_macd(ti)
        st.subheader("RSI")
        st.line_chart(ti.set_index("timestamp")["rsi"])
        st.subheader("MACD")
        st.line_chart(ti.set_index("timestamp")[["macd", "macd_signal"]])

    st.subheader("Trending Coins")
    if trending is not None and not trending.empty:
        st.table(trending)
    else:
        st.info("Trending data unavailable.")

# Tab 1: Compare Coins
with tabs[1]:
    st.header("Compare Current Prices & Correlation")
    symbols = df["symbol"].tolist()
    selected = st.multiselect(
        "Pick coins to compare:",
        options=symbols,
        default=symbols[:3],
        help="Select multiple coins to compare their current price and 24h correlation."
    )
    if selected:
        comp_df = df[df["symbol"].isin(selected)][["symbol", "current_price", "image"]].set_index("symbol")
        cols = st.columns(len(selected))
        for i, sym in enumerate(selected):
            with cols[i]:
                st.image(str(comp_df.loc[sym, "image"]), width=50)
                st.metric(sym, f"${comp_df.loc[sym, 'current_price']:,}")

        corr = df.set_index("symbol")[["price_change_percentage_24h"]]
        corr_mat = corr.loc[selected].corr()
        st.subheader("Correlation Heatmap (24h % change)")
        fig = px.imshow(corr_mat, text_auto=True, aspect="auto")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one coin.")

# Tab 2: Movers & Rankings
with tabs[2]:
    st.header("🚀 Movers & 🏆 Rankings")

    # Top Movers
    st.subheader("Top Movers (24h % Change)")
    st.write("Biggest winners and losers over the past day.")
    movers_cols = st.columns(2)
    gainers = df.nlargest(5, "price_change_percentage_24h")[["symbol", "price_change_percentage_24h", "image"]]
    losers  = df.nsmallest(5, "price_change_percentage_24h")[["symbol", "price_change_percentage_24h", "image"]]

    with movers_cols[0]:
        st.markdown("**Gainers**")
        for _, r in gainers.iterrows():
            st.image(r["image"], width=30, caption=f"{r['symbol']}  +{r['price_change_percentage_24h']:.2f}%")

    with movers_cols[1]:
        st.markdown("**Losers**")
        for _, r in losers.iterrows():
            st.image(r["image"], width=30, caption=f"{r['symbol']}  {r['price_change_percentage_24h']:.2f}%")

    # Alert section
    alerts = df[df["price_change_percentage_24h"].abs() > threshold][["symbol", "price_change_percentage_24h", "image"]]
    if not alerts.empty:
        st.warning(f"⚠️ Moves > {threshold}%")
        for _, r in alerts.iterrows():
            st.write(f"{r['symbol']}: {r['price_change_percentage_24h']:.2f}%")

    st.markdown("---")

    # Top 10 by Market Cap
    st.subheader("Top 10 by Market Cap")
    st.write("The ten largest networks ranked by total market capitalization.")
    top10 = df.nlargest(10, "market_cap")[["symbol", "market_cap", "image"]].set_index("symbol")

    logo_cols = st.columns(10)
    for i, sym in enumerate(top10.index):
        with logo_cols[i]:
            st.image(str(top10.loc[sym, "image"]), width=40)
            st.caption(sym)

    st.bar_chart(top10["market_cap"])

# Tab 3: Portfolio
with tabs[3]:
    st.header("Portfolio Tracker")
    symbols = df["symbol"].tolist()
    selected = st.multiselect(
        "Select coins to track in your portfolio:",
        options=symbols,
        help="Choose coins you own to calculate current P&L."
    )
    holdings = []
    for sym in selected:
        qty = st.number_input(
            f"{sym} quantity",
            min_value=0.0, value=0.0, key=f"{sym}_qty",
            help="Enter how many units of this coin you hold."
        )
        pp = st.number_input(
            f"{sym} purchase price (USD)",
            min_value=0.0, value=0.0, key=f"{sym}_pp",
            help="Enter your average purchase price per coin."
        )
        if qty > 0 and pp > 0:
            cp = float(df[df["symbol"] == sym]["current_price"])
            holdings.append({
                "symbol": sym,
                "quantity": qty,
                "purchase_price": pp,
                "current_price": cp
            })

    if holdings:
        port_df = pd.DataFrame(holdings).set_index("symbol")
        port_df["current_value"] = port_df["quantity"] * port_df["current_price"]
        port_df["cost_basis"]   = port_df["quantity"] * port_df["purchase_price"]
        port_df["pnl_pct"]      = (port_df["current_value"] - port_df["cost_basis"]) / port_df["cost_basis"] * 100
        st.metric("Total Portfolio Value", f"${port_df['current_value'].sum():,.2f}")
        st.table(port_df[["quantity", "purchase_price", "current_price", "current_value", "pnl_pct"]])
        fig_pie = px.pie(port_df, values="current_value", names=port_df.index, title="Allocation")
        st.plotly_chart(fig_pie, use_container_width=True)
