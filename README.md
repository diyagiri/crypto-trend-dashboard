# 📈 Real-Time Crypto Dashboard

A live, interactive Streamlit web app leveraging the free CoinGecko API to visualize and analyze cryptocurrency data in real time.

🔗 **Live Demo:** https://crypto-trend-dashboard-qgaqtk8obbhyg4ye3chrg3.streamlit.app/

## 🚀 Features

- **Global Market Metrics**  
  Total market cap, 24 h cap change, active cryptocurrencies, and BTC dominance.
- **Top Coin Overview**  
  Leader coin’s logo, market cap, 24 h volume, and % change.
- **Trends Tab**  
  - 24 h % change distribution.  
  - Historical price chart (selectable days) with RSI & MACD.  
  - Trending coins list.
- **Compare Coins**  
  - Multi-select price comparison with logos.  
  - Historical price overlay and daily returns correlation heatmap.
- **Movers & Rankings**  
  - Top 5 gainers/losers by 24 h % change with logos.  
  - Top 10 coins by market cap with logos and chart.
- **Portfolio Tracker**  
  - Input hypothetical holdings and purchase prices.  
  - Calculates current value, cost basis, P&L %, and allocation pie.
- **Info Expanders**  
  Contextual tooltips and detailed explanations for beginners.
- **Auto-Refresh**  
  Live data refreshes every 60 seconds via `st_autorefresh`.

## 📁 Project Structure

```
crypto-dashboard/
├── app.py           # Streamlit UI layout (tabs, widgets, charts)
├── data.py          # CoinGecko API fetchers
├── utils.py         # Data processing & technical indicators
├── requirements.txt # Python dependencies
└── README.md        # Project overview & setup guide
```

## ⚙️ Setup & Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/YourUsername/Automating_Crypto_Website_API_Pull.git
   cd Automating_Crypto_Website_API_Pull
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python3 -m venv .env
   source .env/bin/activate        # macOS/Linux
   .env\Scripts\activate         # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally**  
   ```bash
   streamlit run app.py
   ```

5. **View live demo**  
   Open the app in your browser at the link above.

## 📦 Dependencies

- Python 3.7+  
- streamlit  
- pandas  
- requests  
- streamlit-autorefresh  
- plotly  

## 🔮 Future Improvements

- Export chart data as CSV.  
- On-chart hover tooltips for detailed datapoints.  
- WebSocket integration for live order-book depth.  
- Custom domain & theming.

---

**Built with 🐍 Python, 📊 Plotly & Streamlit—showcase your real-time analytics skills!**
