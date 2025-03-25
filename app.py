import streamlit as st
import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
import requests

# --- Page Setup ---
st.set_page_config(
    page_title="Crypto Trend Dashboard 💹",
    page_icon="💹",
    layout="wide"
)

# --- Global Font Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tinos&display=swap');

    * {
        font-family: 'Tinos', serif !important;
    }
    .centered-title {
        text-align: center;
        font-size: 42px;
        color: white !important;
        margin-bottom: 0px;
    }
    .centered-caption {
        text-align: center;
        font-size: 16px;
        color: #AAAAAA !important;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title and Subtitle ---
st.markdown("<h1 class='centered-title'>📊 Simulated Crypto Trend Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered-caption'>A Streamlit web app that simulates real-time cryptocurrency trend analysis using minute-by-minute historical snapshots...</p>", unsafe_allow_html=True)

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

# Friendly metric labels
metric_labels = {
    'quote.USD.price': 'Price (USD)',
    'quote.USD.market_cap': 'Market Cap (USD)',
    'quote.USD.volume_24h': 'Volume (24h, USD)',
    'quote.USD.percent_change_24h': '24h % Change'
}

selected_label = st.sidebar.selectbox("Select Metric", list(metric_labels.values()))
selected_metric = [k for k, v in metric_labels.items() if v == selected_label][0]


# --- Tabs for Navigation ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🔀 Compare Coins", "🚀 Movers", "🏆 Top 10"])

# -------------------------------------------------------------------------------------
# 📈 Tab 1: Price Trend & Volatility
# -------------------------------------------------------------------------------------
# --- Helper function to get trending tokens ---
# --- CoinGecko helper ---
@st.cache_data(ttl=300)
def get_top_trending_tokens(n=5):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": n,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    return pd.DataFrame(response.json())

@st.cache_data(ttl=600)
def get_coin_logo_from_market(selected_coin):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1
    }
    response = requests.get(url, params=params)
    if response.ok:
        market_data = response.json()
        for coin in market_data:
            if coin["name"].lower() == selected_coin.lower():
                return coin["image"]
    return None

with tab1:
    # --- Section Header with Coin Logo ---
    logo_url = get_coin_logo_from_market(selected_coin)
    col_header = st.columns([0.1, 0.9])

    if logo_url:
        with col_header[0]:
            st.image(logo_url, width=40)
    with col_header[1]:
        st.subheader(f"{selected_coin} — {metric_labels.get(selected_metric, selected_metric)} with Rolling Average")

    # --- Prepare Coin Data ---
    coin_df = df[df['name'] == selected_coin].copy()
    coin_df.sort_values('timestamp', inplace=True)
    coin_df['rolling_mean'] = coin_df[selected_metric].rolling(window=5).mean()
    coin_df['volatility'] = coin_df[selected_metric].rolling(window=5).std()

    # --- Metric Line Chart (Interactive) ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=coin_df['timestamp'], y=coin_df[selected_metric],
                             mode='lines+markers', name='Actual', line=dict(color="#8e44ad")))
    fig.add_trace(go.Scatter(x=coin_df['timestamp'], y=coin_df['rolling_mean'],
                             mode='lines', name='5-point Avg', line=dict(color="#00FFAB", dash='dash')))
    fig.update_layout(title=f"{selected_coin} — {metric_labels.get(selected_metric, selected_metric)} Over Time",
                      xaxis_title="Timestamp", yaxis_title=metric_labels.get(selected_metric, selected_metric),
                      template='plotly_dark', legend_title="Metric", hovermode='x unified', height=500)
    st.plotly_chart(fig, use_container_width=True)

    # --- Volatility Chart ---
    st.subheader(f"📉 {selected_coin} — Volatility (Rolling Std Dev)")
    fig2 = px.line(coin_df, x='timestamp', y='volatility',
                   title=f"{selected_coin} — Volatility of {metric_labels.get(selected_metric, selected_metric)}",
                   labels={'timestamp': 'Timestamp', 'volatility': 'Volatility'}, template='plotly_dark')
    fig2.update_traces(line=dict(color='#FFA500'))
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

    # --- Explanation ---
    with st.expander("ℹ️ What does this chart show?"):
        st.markdown(f"""
        - The first chart shows the **{metric_labels.get(selected_metric, selected_metric).lower()}** of **{selected_coin}** over time, along with a **5-point rolling average**.
        - Hover for exact values. The second chart shows rolling **volatility**, which helps identify market turbulence.
        """)

   # --- Trending Tokens (Bottom Section) ---
    st.subheader("🔥 Trending Tokens")
    trending_df = get_top_trending_tokens(5)
    cols = st.columns(5)

    for i, row in trending_df.iterrows():
        with cols[i]:
            st.markdown(f"""
                <div style="
                    background-color: #1e1e1e;
                    padding: 15px;
                    border-radius: 12px;
                    text-align: center;
                    box-shadow: 0 0 10px rgba(255,255,255,0.05);
                    margin-bottom: 15px;
                ">
                    <img src="{row['image']}" style="width:40px;margin-bottom:10px;" />
                    <h4 style='margin:5px 0;'>${row['current_price']:,.3f}</h4>
                    <p style='color:{"#00FFAB" if row["price_change_percentage_24h"] >= 0 else "#FF6B6B"}; font-weight:bold; margin:4px 0;'>
                        {row["price_change_percentage_24h"]:.2f}%
                    </p>
                    <strong style='color:white;'>{row["name"]}</strong><br>
                    <span style='background:#333;padding:2px 6px;border-radius:4px;font-size:12px;color:#ccc;'>
                        {row["symbol"].upper()}
                    </span>
                </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------------------------------
# 🔀 Tab 2: Multi-Coin Comparison
# -------------------------------------------------------------------------------------
with tab2:
    st.subheader("🔀 Compare Multiple Coins by Price")

    selected_coins = st.multiselect("Select Coins to Compare", coin_list, default=['Bitcoin', 'Ethereum'])
    compare_df = df[df['name'].isin(selected_coins)]

    # Cleaned label
    compare_df = compare_df.copy()
    compare_df['price'] = compare_df['quote.USD.price']

    # Plotly line chart
    fig = px.line(
        compare_df,
        x='timestamp',
        y='price',
        color='name',
        title="Interactive Price Comparison Over Time",
        labels={
            'timestamp': 'Time',
            'price': 'Price (USD)',
            'name': 'Coin'
        },
        template='plotly_dark'
    )

    fig.update_traces(mode='lines+markers')  # Add dots to make values easier to hover

    # Layout tweaks
    fig.update_layout(
        height=500,
        xaxis_title="Timestamp",
        yaxis_title="Price (USD)",
        legend_title="Coin",
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("ℹ️ What does this chart show?"):
        st.markdown(f"""
        - This interactive chart shows **price trends** of the selected coins over time.
        - You can **hover over lines** to see exact price values at each timestamp.
        - You can also **zoom in, pan**, or export the chart using the toolbar.
        - Helps compare coins even when they vary in magnitude (e.g., BTC vs. SHIB).
        """)

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

        top_gainers = merged.nlargest(5, 'pct_change').sort_values('pct_change')
        top_losers = merged.nsmallest(5, 'pct_change').sort_values('pct_change')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("🚀 **Top Gainers**")
            fig_gainers = px.bar(
                top_gainers,
                x='pct_change',
                y='name',
                orientation='h',
                text=top_gainers['pct_change'].map("{:.2f}%".format),
                color='pct_change',
                color_continuous_scale=[
                    "#b6e2b6",  # light green
                    "#78d678",  # medium green
                    "#006400"   # dark green
                ],
                range_color=[top_gainers['pct_change'].min(), top_gainers['pct_change'].max()]
            )
            fig_gainers.update_layout(
                xaxis_title="Percentage Change",
                yaxis_title="Coin",
                template="plotly_dark",
                height=300,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_gainers, use_container_width=True)

        with col2:
            st.markdown("📉 **Top Losers**")
            fig_losers = px.bar(
                top_losers,
                x='pct_change',
                y='name',
                orientation='h',
                text=top_losers['pct_change'].map("{:.2f}%".format),
                color='pct_change',
                color_continuous_scale=[
                    "#8b0000",  # darkest red (for biggest loss)
                    "#e74c3c",
                    "#ffb3b3",  # lightest red (for smallest loss)
                ],
                range_color=[top_losers['pct_change'].min(), top_losers['pct_change'].max()]
            )
            fig_losers.update_layout(
                xaxis_title="Percentage Change",
                yaxis_title="Coin",
                template="plotly_dark",
                height=300,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_losers, use_container_width=True)


        # Trend Alerts
        st.subheader("🚨 Trend Alerts")
        threshold = st.slider("Alert Threshold (%)", 0.1, 10.0, 5.0)
        alerts = merged[merged['pct_change'].abs() > threshold]

        if not alerts.empty:
            st.warning("Coins with significant movement:")
            fig_alerts = px.bar(
                alerts.sort_values('pct_change'),
                x='pct_change',
                y='name',
                orientation='h',
                text=alerts['pct_change'].map("{:.2f}%".format),
                color='pct_change',
                color_continuous_scale=[
                    '#FF6B6B', '#FF7C7C', '#999', '#00FFAB', '#00D78D'
                ],
            )
            fig_alerts.update_layout(
                xaxis_title="Percentage Change",
                yaxis_title="Coin",
                template="plotly_dark",
                height=300,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_alerts, use_container_width=True)
        else:
            st.success("No coins exceeded the threshold.")
    else:
        st.info("Not enough snapshots in the last 10 minutes to calculate top movers.")

# -------------------------------------------------------------------------------------
# 🏆 Tab 4: Top 10 Coins by Price, Volume, Market Cap
# -------------------------------------------------------------------------------------

with tab4:
    st.subheader("💰 Top 10 Coins by Price, Volume, and Market Cap")

    # Helper to attach logo URLs
    @st.cache_data(ttl=600)
    def get_market_data_with_logos():
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1
        }
        r = requests.get(url, params=params)
        if r.ok:
            return pd.DataFrame(r.json())
        return pd.DataFrame()

    market_df = get_market_data_with_logos()

    # Merge logos into df_latest
    merged = pd.merge(df_latest, market_df[['name', 'image']], on='name', how='left')

    def plot_top10(data, column, title, color):
        top10 = data.nlargest(10, column).sort_values(by=column)
        fig = px.bar(
            top10,
            x=column,
            y=top10['name'].apply(lambda x: f"<b>{x}</b>"),
            orientation='h',
            text=top10[column].map("${:,.0f}".format),
            color_discrete_sequence=[color],
        )
        fig.update_traces(marker_line_width=1.5, textposition='outside')

        # Add logos as custom hover
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>' + f"{column.replace('quote.USD.', '').replace('_', ' ').title()}: " + '%{x:,.0f}'
        )

        fig.update_layout(
            template="plotly_dark",
            title=title,
            height=400,
            yaxis=dict(showgrid=False, showline=False, title=None),
            xaxis=dict(title=None),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig

    col1, col2 = st.columns(2)
    with col1:
        fig_price = plot_top10(merged, 'quote.USD.price', "💰 Top 10 by Price", "#6A5ACD")
        st.plotly_chart(fig_price, use_container_width=True)

    with col2:
        fig_volume = plot_top10(merged, 'quote.USD.volume_24h', "📦 Top 10 by 24h Volume", "#00CED1")
        st.plotly_chart(fig_volume, use_container_width=True)

    fig_marketcap = plot_top10(merged, 'quote.USD.market_cap', "🏦 Top 10 by Market Cap", "#FF8C00")
    st.plotly_chart(fig_marketcap, use_container_width=True)

    # About
    with st.expander("ℹ️ About this app"):
        st.markdown("""
        - This dashboard pulls cryptocurrency data every minute using the CoinMarketCap API.
        - Snapshots are saved in the `snapshots/` folder and loaded for analysis.
        - You can explore trends, compare coins, monitor market volatility, and detect top movers in real time.
        - Built with 🐍 Python, 🧼 Pandas, 📊 Plotly, and 🚀 Streamlit.
        """)
