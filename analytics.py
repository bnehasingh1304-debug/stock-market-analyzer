"""
Financial Analytics Module containing the 5 MongoDB Financial Queries.
"""
import logging
import os
import pandas as pd
import numpy as np
from pymongo import DESCENDING, ASCENDING
import config
from database import db_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class FinancialAnalytics:
    def __init__(self, db=None):
        self.collection = db_manager.get_collection() if db is None else db

    def _get_data_df(self):
        """Helper returning full dataset as DataFrame from database or backup CSV."""
        db_manager._auto_seed_if_empty()
        docs = list(self.collection.find({}, {"_id": 0}))
        if docs:
            df = pd.DataFrame(docs)
        else:
            backup_file = os.path.join(config.DATA_DIR, "stock_data_backup.csv")
            if os.path.exists(backup_file):
                df = pd.read_csv(backup_file)
            else:
                df = pd.DataFrame()
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df

    def query_1_moving_averages(self, ticker="AAPL", limit=100):
        """Query 1: 30-Day Moving Average & Closing Price Trend for a given ticker."""
        logger.info(f"Executing Query 1: 30-Day Moving Average for {ticker}...")
        df = self._get_data_df()
        if df.empty:
            return pd.DataFrame()
        
        filtered = df[df['ticker'] == ticker].sort_values(by="date", ascending=False).head(limit)
        if not filtered.empty:
            filtered = filtered.sort_values(by="date").reset_index(drop=True)
            cols = [c for c in ['ticker', 'date', 'close', 'sma_30', 'daily_return'] if c in filtered.columns]
            return filtered[cols]
        return pd.DataFrame()

    def query_2_highest_single_day_gains(self, top_n=10):
        """Query 2: Top Highest Single-Day Percentage Gains across all tickers."""
        logger.info("Executing Query 2: Highest Single-Day Percentage Gain...")
        df = self._get_data_df()
        if df.empty:
            return pd.DataFrame()
        
        top_df = df.sort_values(by="daily_return", ascending=False).head(top_n)
        cols = [c for c in ['ticker', 'date', 'open', 'close', 'daily_return', 'volume'] if c in top_df.columns]
        return top_df[cols].reset_index(drop=True)

    def query_3_volatility_ranking(self):
        """Query 3: Volatility Ranking Table (Standard Deviation of Daily Returns per Stock)."""
        logger.info("Executing Query 3: Stock Volatility Ranking...")
        df = self._get_data_df()
        if df.empty:
            return pd.DataFrame()

        grouped = df.groupby("ticker")["daily_return"].agg(
            volatility_std_dev="std",
            avg_return="mean",
            min_return="min",
            max_return="max",
            total_records="count"
        ).reset_index()
        res = grouped.round(4).sort_values(by="volatility_std_dev", ascending=False)
        return res.reset_index(drop=True)

    def query_4_stock_correlation(self, tickers=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMZN"]):
        """Query 4: Stock Price Return Correlation Matrix among selected tickers."""
        logger.info(f"Executing Query 4: Stock Correlation Matrix for {tickers}...")
        df = self._get_data_df()
        if df.empty:
            return pd.DataFrame()
            
        filtered = df[df['ticker'].isin(tickers)]
        if filtered.empty:
            return pd.DataFrame()
            
        pivot_df = filtered.pivot(index="date", columns="ticker", values="daily_return")
        corr_matrix = pivot_df.corr().round(4)
        return corr_matrix

    def query_5_best_worst_performers(self):
        """Query 5: Best & Worst Performing Stocks over the entire dataset timeframe (Cumulative Returns)."""
        logger.info("Executing Query 5: Best & Worst Performing Stocks...")
        df = self._get_data_df()
        if df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        df_sorted = df.sort_values(by="date")
        summary = []
        for t, g in df_sorted.groupby("ticker"):
            if g.empty:
                continue
            init_p = g['open'].iloc[0]
            last_p = g['close'].iloc[-1]
            if init_p == 0:
                continue
            cum_ret = round(((last_p - init_p) / init_p) * 100.0, 2)
            summary.append({
                "ticker": t,
                "initial_price": init_p,
                "latest_price": last_p,
                "cumulative_return_pct": cum_ret
            })
        res_df = pd.DataFrame(summary).sort_values(by="cumulative_return_pct", ascending=False)
        return res_df, res_df.head(5), res_df.tail(5)

    def get_time_series_comparison(self, tickers=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]):
        """Retrieves historical price comparison series for 3-5 tickers."""
        df = self._get_data_df()
        if df.empty:
            return pd.DataFrame()
            
        filtered = df[df['ticker'].isin(tickers)]
        if filtered.empty:
            return pd.DataFrame()
            
        pivot_df = filtered.pivot(index="date", columns="ticker", values="close")
        return pivot_df

analytics_engine = FinancialAnalytics()
