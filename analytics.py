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

    def query_1_moving_averages(self, ticker="AAPL", limit=100):
        """Query 1: 30-Day Moving Average & Closing Price Trend for a given ticker."""
        logger.info(f"Executing Query 1: 30-Day Moving Average for {ticker}...")
        cursor = self.collection.find(
            {"ticker": ticker},
            {"_id": 0, "ticker": 1, "date": 1, "close": 1, "sma_30": 1, "daily_return": 1}
        ).sort("date", DESCENDING).limit(limit)
        
        results = list(cursor)
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(by="date").reset_index(drop=True)
        return df

    def query_2_highest_single_day_gains(self, top_n=10):
        """Query 2: Top Highest Single-Day Percentage Gains across all tickers."""
        logger.info("Executing Query 2: Highest Single-Day Percentage Gain...")
        cursor = self.collection.find(
            {},
            {"_id": 0, "ticker": 1, "date": 1, "open": 1, "close": 1, "daily_return": 1, "volume": 1}
        ).sort("daily_return", DESCENDING).limit(top_n)
        
        results = list(cursor)
        return pd.DataFrame(results)

    def query_3_volatility_ranking(self):
        """Query 3: Volatility Ranking Table (Standard Deviation of Daily Returns per Stock)."""
        logger.info("Executing Query 3: Stock Volatility Ranking...")
        
        if not db_manager.is_mock:
            try:
                pipeline = [
                    {
                        "$group": {
                            "_id": "$ticker",
                            "std_dev_return": {"$stdDevPop": "$daily_return"},
                            "avg_daily_return": {"$avg": "$daily_return"},
                            "min_return": {"$min": "$daily_return"},
                            "max_return": {"$max": "$daily_return"},
                            "total_records": {"$sum": 1}
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "ticker": "$_id",
                            "volatility_std_dev": {"$round": ["$std_dev_return", 4]},
                            "avg_return": {"$round": ["$avg_daily_return", 4]},
                            "min_return": {"$round": ["$min_return", 4]},
                            "max_return": {"$round": ["$max_return", 4]},
                            "total_records": 1
                        }
                    },
                    {"$sort": {"volatility_std_dev": -1}}
                ]
                results = list(self.collection.aggregate(pipeline))
                df = pd.DataFrame(results)
                if not df.empty:
                    return df
            except Exception as e:
                logger.warning(f"MongoDB pipeline notice: {e}. Switching to fast fallback...")

        # Fast pandas calculation using local data backup
        backup_file = os.path.join(config.DATA_DIR, "stock_data_backup.csv")
        if os.path.exists(backup_file):
            raw_df = pd.read_csv(backup_file)
        else:
            raw_df = pd.DataFrame(list(self.collection.find({}, {"_id": 0, "ticker": 1, "daily_return": 1})))

        if raw_df.empty:
            return pd.DataFrame()

        grouped = raw_df.groupby("ticker")["daily_return"].agg(
            volatility_std_dev="std",
            avg_return="mean",
            min_return="min",
            max_return="max",
            total_records="count"
        ).reset_index()
        df = grouped.round(4).sort_values(by="volatility_std_dev", ascending=False)
        return df

    def query_4_stock_correlation(self, tickers=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMZN"]):
        """Query 4: Stock Price Return Correlation Matrix among selected tickers."""
        logger.info(f"Executing Query 4: Stock Correlation Matrix for {tickers}...")
        cursor = self.collection.find(
            {"ticker": {"$in": tickers}},
            {"_id": 0, "ticker": 1, "date": 1, "daily_return": 1}
        )
        results = list(cursor)
        df = pd.DataFrame(results)
        if df.empty:
            return pd.DataFrame()
            
        pivot_df = df.pivot(index="date", columns="ticker", values="daily_return")
        corr_matrix = pivot_df.corr().round(4)
        return corr_matrix

    def query_5_best_worst_performers(self):
        """Query 5: Best & Worst Performing Stocks over the entire dataset timeframe (Cumulative Returns)."""
        logger.info("Executing Query 5: Best & Worst Performing Stocks...")
        
        if not db_manager.is_mock:
            try:
                pipeline = [
                    {"$sort": {"date": 1}},
                    {
                        "$group": {
                            "_id": "$ticker",
                            "initial_price": {"$first": "$open"},
                            "latest_price": {"$last": "$close"}
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "ticker": "$_id",
                            "initial_price": 1,
                            "latest_price": 1,
                            "cumulative_return_pct": {
                                "$round": [
                                    {"$multiply": [{"$divide": [{"$subtract": ["$latest_price", "$initial_price"]}, "$initial_price"]}, 100]},
                                    2
                                ]
                            }
                        }
                    },
                    {"$sort": {"cumulative_return_pct": -1}}
                ]
                results = list(self.collection.aggregate(pipeline))
                df = pd.DataFrame(results)
                if not df.empty:
                    return df, df.head(5), df.tail(5)
            except Exception as e:
                logger.warning(f"MongoDB pipeline notice: {e}. Switching to fast fallback...")

        # Fast pandas calculation using local data backup
        backup_file = os.path.join(config.DATA_DIR, "stock_data_backup.csv")
        if os.path.exists(backup_file):
            raw_df = pd.read_csv(backup_file)
        else:
            raw_df = pd.DataFrame(list(self.collection.find({}, {"_id": 0, "ticker": 1, "date": 1, "open": 1, "close": 1})))

        if raw_df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        raw_df = raw_df.sort_values(by="date")
        summary = []
        for t, g in raw_df.groupby("ticker"):
            init_p = g['open'].iloc[0]
            last_p = g['close'].iloc[-1]
            cum_ret = round(((last_p - init_p) / init_p) * 100.0, 2)
            summary.append({
                "ticker": t,
                "initial_price": init_p,
                "latest_price": last_p,
                "cumulative_return_pct": cum_ret
            })
        df = pd.DataFrame(summary).sort_values(by="cumulative_return_pct", ascending=False)
        return df, df.head(5), df.tail(5)

    def get_time_series_comparison(self, tickers=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]):
        """Retrieves historical price comparison series for 3-5 tickers."""
        cursor = self.collection.find(
            {"ticker": {"$in": tickers}},
            {"_id": 0, "ticker": 1, "date": 1, "close": 1}
        )
        results = list(cursor)
        df = pd.DataFrame(results)
        if not df.empty:
            pivot_df = df.pivot(index="date", columns="ticker", values="close")
            return pivot_df
        return pd.DataFrame()

analytics_engine = FinancialAnalytics()
