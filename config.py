"""
Configuration settings for Stock Market Tick Data Analyzer
"""
import os

# Project Root Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "stock_market_db"
COLLECTION_NAME = "tick_data"

# Stock Tickers (S&P 500 & Top Tech, Finance, Healthcare, Energy, Retail)
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "WMT",
    "UNH", "MA", "PG", "JNJ", "HD", "XOM", "BAC", "ABBV", "COST", "CVX",
    "MRK", "DIS", "PEP", "CSCO", "KO", "ACN", "ADBE", "LIN", "TMO", "WFC",
    "MCD", "CRM", "AMD", "TXN", "PM", "NFLX", "ABT", "ORCL", "GE", "DHR",
    "INTU", "CAT", "IBM", "BKNG", "AMAT", "QCOM", "UNP", "NOW", "SPGI", "BA",
    "HON", "GS", "AMGN", "VZ", "LLY", "COP", "MS", "SYK", "ISRG", "NKE",
    "LOW", "RTX", "MDLZ", "AXP", "T", "PLD", "TJX", "BLK", "DE", "ADP",
    "MMC", "SCHW", "AMT", "C", "ADI", "ZTS", "LMT", "GILD", "FI", "SBUX"
]

# Time Period Settings
START_DATE = "2018-01-01"
END_DATE = "2026-01-01"

# Output Paths
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
DATA_DIR = os.path.join(BASE_DIR, "data")

for directory in [CHARTS_DIR, REPORTS_DIR, DATA_DIR]:
    os.makedirs(directory, exist_ok=True)
