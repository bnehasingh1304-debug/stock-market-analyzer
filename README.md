# 📈 Stock Market Tick Data Analyzer

> **Enterprise MongoDB Time-Series & High-Frequency Stock Data Analytics System**

---

### 🚀 Live Web Deployment Link (GitHub Pages):
👉 **[https://bnehasingh1304-debug.github.io/stock-market-analyzer/](https://bnehasingh1304-debug.github.io/stock-market-analyzer/)**

### 📁 GitHub Repository Link:
👉 **[https://github.com/bnehasingh1304-debug/stock-market-analyzer](https://github.com/bnehasingh1304-debug/stock-market-analyzer)**

---

## 🌟 Key Features

- **Scalable MongoDB Database**: Stores **100,000+ records** across 80+ stock tickers over 8 years of trading history.
- **High-Performance Compound Indexing**: Optimized compound indexes on `(ticker, date)` for sub-millisecond aggregations.
- **5 Core Financial Queries**:
  1. **30-Day Moving Average (SMA & EMA)**: Computes price trends and smoothing overlays.
  2. **Highest Single-Day Gainers**: Identifies max percentage single-day jumps across all assets.
  3. **Volatility Ranking Table**: Calculates daily return standard deviation to rank stock risk.
  4. **Stock Return Correlation Matrix**: Analyzes asset co-movement and diversification efficiency.
  5. **Best & Worst Performing Stocks**: Computes total cumulative return percentages.
- **HTML5 Web Dashboard**: Built with HTML5, CSS3, Bootstrap, and Chart.js line graphs (`index.html`).
- **Automated PDF Project Report Generator**: Uses ReportLab to compile a publication-ready PDF report containing schema specs, query tables, visual charts, and investment insights.

---

## 🏗️ Project Architecture & Directory Structure

```text
stock-market-analyzer/
├── config.py             # Global configurations, ticker list, MongoDB URI, directory paths
├── database.py           # MongoDB connection management, schema indexing & mongomock fallback
├── data_ingestion.py     # yfinance API harvester and MongoDB bulk insertion engine
├── analytics.py          # 5 MongoDB financial aggregation queries
├── visualizer.py         # Matplotlib and Seaborn visualization charts
├── report_generator.py   # Publication-quality PDF report builder (ReportLab)
├── index.html            # Standalone HTML5 web application dashboard
├── main.py               # Master CLI execution pipeline script
├── run_project.bat       # Windows double-clickable launcher menu
├── Launch_Website.bat    # Windows 1-click web launcher
├── HOW_TO_RUN.md         # Step-by-step instructions to open and run anytime
├── requirements.txt      # Python dependencies for deployment
├── charts/               # Output directory for generated chart PNGs
├── reports/              # Output directory for generated PDF reports
└── data/                 # Local data cache and CSV backups
```

---

## 🚀 Quick Start Instructions

1. **Run Full Pipeline (Fetch Data, Seed Database, Execute Queries, Build PDF)**:
   ```bash
   python main.py
   ```

2. **Open HTML5 Web Application**:
   Double-click `index.html` or open `http://localhost:5000` (`python server.py`).

---

## 📑 Database Schema Definition

```json
{
  "ticker": "AAPL",
  "date": "2024-01-15T00:00:00.000Z",
  "open": 185.20,
  "high": 187.50,
  "low": 184.80,
  "close": 186.90,
  "volume": 52431000,
  "daily_return": 0.9179,
  "sma_30": 183.45,
  "volatility_30": 1.12
}
```
