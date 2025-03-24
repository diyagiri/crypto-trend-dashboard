import streamlit as st
import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt

# --- Page Setup ---
st.set_page_config(
    page_title="Crypto Trend Dashboard 💹",
    page_icon="💹",
    layout="wide"
)

st.title("📊 Real-Time Crypto Trend Analysis Dashboard")
st.caption("Stay updated with live price, volume, and market cap data — refreshed every minute.")

# --- Load Data ---
@st.cache_data
def load_data():
    files = sorted(glob.glob("snapshots/snapshot_*.csv"))
    df_list = [pd.read_csv(file) for file in files]
    df_all = pd.concat(df_list, ignore_index=True)
    df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
    return df_all

df = load_data()
latest_timestamp = df['timestamp'].max()
df_latest = df[df['timestamp'] == latest_timestamp]

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")
coin_list = df['name'].unique()
selected_coin = st.sidebar.selectbox("Select a Coin", coin_list)
selected_metric = st.sidebar.selectbox("Select Metric", [
    'quote.USD.price',
    'quote.USD.market_cap',
    'quote.USD.volume_24h',
    'quote.USD.percent_change_24h'
])

# --- Tabs for Navigation ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🔀 Compare Coins", "🚀 Movers", "🏆 Top 10"])

# -------------------------------------------------------------------------------------
# 📈 Tab 1: Price Trend & Volatility
# -------------------------------------------------------------------------------------
with tab1:
    st.subheader(f"📈 {selected_coin} — {selected_metric} with Rolling Average")

    coin_df = df[df['name'] == selected_coin].copy()
    coin_df.sort_values('timestamp', inplace=True)
    coin_df['rolling_mean'] = coin_df[selected_metric].rolling(window=5).mean()
    coin_df['volatility'] = coin_df[selected_metric].rolling(window=5).std()

    latest = coin_df.iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Price", f"${latest['quote.USD.price']:.2f}")
    col2.metric("24h Change", f"{latest['quote.USD.percent_change_24h']:.2f}%")
    col3.metric("Market Cap", f"${latest['quote.USD.market_cap']:.2f}")

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=coin_df, x='timestamp', y=selected_metric, label='Actual', ax=ax)
    sns.lineplot(data=coin_df, x='timestamp', y='rolling_mean', label='5-min Avg', ax=ax)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader(f"📉 {selected_coin} — Volatility (Rolling Std Dev)")
    fig2, ax2 = plt.subplots(figsize=(12, 3))
    sns.lineplot(data=coin_df, x='timestamp', y='volatility', ax=ax2, color='orange')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig2)

# -------------------------------------------------------------------------------------
# 🔀 Tab 2: Multi-Coin Comparison
# -------------------------------------------------------------------------------------
with tab2:
    st.subheader("🔀 Compare Multiple Coins")
    selected_coins = st.multiselect("Select Coins to Compare", coin_list, default=['Bitcoin', 'Ethereum'])
    compare_df = df[df['name'].isin(selected_coins)]
    
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=compare_df, x='timestamp', y='quote.USD.price', hue='name', ax=ax3)
    ax3.set_ylabel("Price (USD)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig3)

# -------------------------------------------------------------------------------------
# 🚀 Tab 3: Top Gainers/Losers & Trend Alerts
# -------------------------------------------------------------------------------------
with tab3:
    st.subheader("📊 Top Gainers & Losers (Last 10 Minutes)")
    window_df = df[df['timestamp'] >= latest_timestamp - pd.Timedelta(minutes=10)]

    if len(window_df['timestamp'].unique()) >= 2:
        last_snap = window_df[window_df['timestamp'] == window_df['timestamp'].max()]
        prev_snap = window_df[window_df['timestamp'] == window_df['timestamp'].unique()[-2]]

        merged = pd.merge(
            last_snap[['name', 'quote.USD.price']],
            prev_snap[['name', 'quote.USD.price']],
            on='name',
            suffixes=('_new', '_old')
        )
        merged['pct_change'] = ((merged['quote.USD.price_new'] - merged['quote.USD.price_old']) / merged['quote.USD.price_old']) * 100

        top_gainers = merged.nlargest(5, 'pct_change')
        top_losers = merged.nsmallest(5, 'pct_change')

        col1, col2 = st.columns(2)
        with col1:
            st.write("🚀 Top Gainers")
            st.dataframe(top_gainers[['name', 'pct_change']].style.format({'pct_change': '{:.2f}%'}))

        with col2:
            st.write("📉 Top Losers")
            st.dataframe(top_losers[['name', 'pct_change']].style.format({'pct_change': '{:.2f}%'}))

        # Trend Alerts
        st.subheader("🚨 Trend Alerts")
        threshold = st.slider("Alert Threshold (%)", 0.1, 10.0, 5.0)
        alerts = merged[merged['pct_change'].abs() > threshold]

        if not alerts.empty:
            st.warning("Coins with significant movement:")
            st.dataframe(alerts[['name', 'pct_change']].style.format({'pct_change': '{:.2f}%'}))
        else:
            st.success("No coins exceeded the threshold.")
    else:
        st.info("Not enough snapshots in the last 10 minutes to calculate top movers.")

# -------------------------------------------------------------------------------------
# 🏆 Tab 4: Top 10 Coins by Price, Volume, Market Cap
# -------------------------------------------------------------------------------------
with tab4:
    st.subheader("💰 Top 10 by Price")
    top10_price = df_latest.nlargest(10, 'quote.USD.price')
    fig1, ax1 = plt.subplots()
    sns.barplot(data=top10_price, y='name', x='quote.USD.price', ax=ax1)
    ax1.set_xlabel("Price (USD)")
    st.pyplot(fig1)

    st.subheader("📦 Top 10 by 24h Volume")
    top10_volume = df_latest.nlargest(10, 'quote.USD.volume_24h')
    fig2, ax2 = plt.subplots()
    sns.barplot(data=top10_volume, y='name', x='quote.USD.volume_24h', ax=ax2)
    ax2.set_xlabel("24h Volume (USD)")
    st.pyplot(fig2)

    st.subheader("🏦 Top 10 by Market Cap")
    top10_marketcap = df_latest.nlargest(10, 'quote.USD.market_cap')
    fig3, ax3 = plt.subplots()
    sns.barplot(data=top10_marketcap, y='name', x='quote.USD.market_cap', ax=ax3)
    ax3.set_xlabel("Market Cap (USD)")
    st.pyplot(fig3)

    # About
    with st.expander("ℹ️ About this app"):
        st.markdown("""
        - This dashboard pulls cryptocurrency data every minute using the CoinMarketCap API.
        - Snapshots are saved in the `snapshots/` folder and loaded for analysis.
        - You can explore trends, compare coins, monitor market volatility, and detect top movers in real time.
        - Built with 🐍 Python, 🧼 Pandas, 📊 Seaborn, and 🚀 Streamlit.
        """)
