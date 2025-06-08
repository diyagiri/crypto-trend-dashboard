# 📈 Real-Time Crypto Dashboard

A live, interactive Streamlit web app leveraging the free CoinGecko API to visualize and analyze cryptocurrency data in real time.

## 🚀 Features

- **Global Market Metrics**  
  Total market cap, 24 h cap change, active cryptocurrencies, and BTC dominance.

- **Top Coin Overview**  
  Displays the leading coin’s logo, name, market cap, 24 h volume, and 24 h % change.

- **Trends Tab**  
  - Bar chart of 24 h % change distribution.  
  - Historical price chart (selectable days) with RSI & MACD technical indicators.  
  - Today’s trending coins.

- **Compare Coins**  
  - Multi-select current price comparison with coin logos.  
  - Correlation heatmap of 24 h % changes.

- **Movers & Rankings**  
  - Top 5 gainers and losers (24 h % change) with logos.  
  - Top 10 coins by market cap, displayed with logos and bar chart.

- **Portfolio Tracker**  
  - Input your holdings and purchase prices.  
  - Calculates current value, cost basis, P&L %, and shows allocation pie chart.

- **Interactive Help**  
  Hover over the “?” icons on sliders and selectors to see context-sensitive tooltips.

- **Auto-Refresh**  
  Data reloads every 60 seconds via `st_autorefresh` for truly live updates.

## 🔧 Project Structure

```
crypto-dashboard/
├── app.py           # Streamlit UI layout (tabs, widgets, charts)
├── data.py          # Data‐fetching functions (CoinGecko API calls)
├── utils.py         # Data processing & technical indicators (RSI, MACD, formatting)
├── requirements.txt # Python dependencies
└── README.md        # Project overview & setup guide
```

## ⚙️ Setup & Installation

1. **Clone the repository**  
   ```bash
   git clone <your-repo-url>
   cd crypto-dashboard
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python3 -m venv .env
   source .env/bin/activate        # macOS/Linux
   .env\Scriptsctivate           # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**  
   ```bash
   streamlit run app.py
   ```

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
- Theme toggle (light/dark).  

---

Built with 🐍 Python, 📊 Plotly & Streamlit—perfect for showcasing real-time analytics in your portfolio!
