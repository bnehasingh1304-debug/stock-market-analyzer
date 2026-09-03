"""
Visualization module generating charts and heatmap plots saved into the charts/ directory.
"""
import os
import logging
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import config
from analytics import analytics_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Set standard visual styling
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

def plot_stock_price_comparison(tickers=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]):
    """Plots stock price line chart comparison over time for 3-5 tickers."""
    logger.info(f"Generating stock price comparison chart for {tickers}...")
    pivot_df = analytics_engine.get_time_series_comparison(tickers)
    
    if pivot_df.empty:
        logger.warning("No data available for stock comparison plot.")
        return None

    plt.figure(figsize=(12, 6))
    for ticker in pivot_df.columns:
        plt.plot(pivot_df.index, pivot_df[ticker], label=ticker, linewidth=1.8)

    plt.title("Stock Price Performance Comparison Over Time", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Date", fontsize=11, fontweight='bold')
    plt.ylabel("Closing Price (USD $)", fontsize=11, fontweight='bold')
    plt.legend(title="Tickers", loc="upper left", frameon=True)
    plt.tight_layout()

    output_path = os.path.join(config.CHARTS_DIR, "stock_comparison.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved stock comparison chart to {output_path}")
    return output_path

def plot_volatility_ranking(top_n=15):
    """Plots bar chart of the top N most volatile stocks."""
    logger.info(f"Generating volatility ranking chart for top {top_n} stocks...")
    df = analytics_engine.query_3_volatility_ranking()
    
    if df.empty:
        logger.warning("No data available for volatility ranking plot.")
        return None

    top_df = df.head(top_n).sort_values(by="volatility_std_dev", ascending=True)

    plt.figure(figsize=(10, 6))
    bars = plt.barh(top_df['ticker'], top_df['volatility_std_dev'], color='#e74c3c', edgecolor='black', alpha=0.85)

    plt.title(f"Top {top_n} Most Volatile Stocks (Daily Return Std Dev)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Daily Return Standard Deviation (%)", fontsize=11, fontweight='bold')
    plt.ylabel("Stock Ticker", fontsize=11, fontweight='bold')

    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.05, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', 
                 va='center', ha='left', fontsize=9, fontweight='bold')

    plt.tight_layout()
    output_path = os.path.join(config.CHARTS_DIR, "volatility_ranking.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved volatility ranking chart to {output_path}")
    return output_path

def plot_correlation_heatmap(tickers=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMZN", "META"]):
    """Plots stock return correlation heatmap."""
    logger.info("Generating stock correlation matrix heatmap...")
    corr_df = analytics_engine.query_4_stock_correlation(tickers)

    if corr_df.empty:
        logger.warning("No data available for correlation heatmap.")
        return None

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_df, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f", linewidths=0.5, cbar_kws={"label": "Correlation Coefficient"})
    plt.title("Stock Daily Return Correlation Matrix", fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()

    output_path = os.path.join(config.CHARTS_DIR, "correlation_matrix.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved correlation matrix heatmap to {output_path}")
    return output_path

def plot_moving_average(ticker="AAPL"):
    """Plots closing price alongside 30-day moving average."""
    logger.info(f"Generating 30-day moving average chart for {ticker}...")
    df = analytics_engine.query_1_moving_averages(ticker=ticker, limit=252)

    if df.empty:
        logger.warning("No data available for moving average plot.")
        return None

    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['close'], label=f"{ticker} Close Price", color='#2980b9', linewidth=1.5)
    plt.plot(df['date'], df['sma_30'], label="30-Day Moving Average (SMA)", color='#e67e22', linewidth=2.0, linestyle='--')

    plt.title(f"{ticker} - 30-Day Moving Average Analysis", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Date", fontsize=11, fontweight='bold')
    plt.ylabel("Price (USD $)", fontsize=11, fontweight='bold')
    plt.legend(loc="upper left")
    plt.tight_layout()

    output_path = os.path.join(config.CHARTS_DIR, f"{ticker}_moving_avg.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved moving average chart to {output_path}")
    return output_path

def generate_all_charts():
    """Generates all visual chart artifacts."""
    c1 = plot_stock_price_comparison()
    c2 = plot_volatility_ranking()
    c3 = plot_correlation_heatmap()
    c4 = plot_moving_average("AAPL")
    return [c1, c2, c3, c4]

if __name__ == "__main__":
    generate_all_charts()
