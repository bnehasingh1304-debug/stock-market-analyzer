# How to Open and Run Your Stock Market Tick Data Analyzer

This guide explains how you can easily open, execute, and explore your project **whenever you want**.

---

## 📁 Where Your Project is Located

Your project is saved at:
`C:\Users\bneha\Documents\stock-market-analyzer\`

---

## 🚀 Option 1: Double-Click Launcher (Easiest Way)

1. Open File Explorer and navigate to:
   `C:\Users\bneha\Documents\stock-market-analyzer\`
2. Double-click **`Launch_Website.bat`** (or **`run_project.bat`**).
3. Your web browser will automatically open your HTML5 website at **`http://localhost:5000`**!

---

## 💻 Option 2: Opening via Command Prompt / PowerShell

Open Command Prompt or PowerShell and run:

```cmd
cd C:\Users\bneha\Documents\stock-market-analyzer
```

### To run the full backend pipeline & generate PDF report:
```cmd
python main.py
```

### To open the HTML5 Web Application:
```cmd
python server.py
```
Then open your web browser to `http://localhost:5000`.

---

## 🛠️ Option 3: Opening in VS Code or Your Favorite Code Editor

1. Open **VS Code** (or PyCharm / Cursor).
2. Click **File -> Open Folder...**
3. Select `C:\Users\bneha\Documents\stock-market-analyzer`.
4. Open the integrated terminal (`Ctrl + ~`) and type:
   - `python main.py` to run the data pipeline.
   - `python server.py` to launch the HTML5 web server.

---

## 📊 Outputs & Deliverables Included

1. **MongoDB Collection**: Standard/Time-series collection with 100,000+ OHLCV stock price documents.
2. **5 Financial Analysis Queries**:
   - 30-Day Moving Average & Price Trends
   - Highest Single-Day Gainers & Losers
   - Stock Volatility Ranking Table (Daily Return Standard Deviation)
   - Stock Price Correlation Matrix
   - Best & Worst Performing Stocks (Cumulative Return)
3. **Visual Charts**: Saved under the `charts/` directory (`stock_comparison.png`, `volatility_ranking.png`, `correlation_matrix.png`, etc.).
4. **PDF Project Report**: Saved at `reports/Stock_Market_Analyzer_Report.pdf`.
