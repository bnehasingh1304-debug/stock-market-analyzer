"""
Master Execution Script for Stock Market Tick Data Analyzer.
Runs ingestion, analytics queries, chart generation, and PDF report creation.
"""
import os
import sys
import logging
import pandas as pd

import config
from database import db_manager
from data_ingestion import fetch_stock_data, populate_mongodb
from analytics import analytics_engine
import visualizer
from report_generator import PDFReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    print("=" * 70)
    print("      STOCK MARKET TICK DATA ANALYZER - MAIN PIPELINE")
    print("=" * 70)
    
    # 1. Database Setup & Indexing
    print("\n[Step 1/5] Initializing MongoDB Connection & Indexes...")
    db_manager.setup_indexes()
    
    current_count = db_manager.count_records()
    print(f"Current record count in MongoDB: {current_count:,}")
    
    # 2. Data Ingestion (Guaranteeing 100,000+ records)
    if current_count < 100000:
        print("\n[Step 2/5] Ingesting stock market data via yfinance (Target: 100,000+ records)...")
        df = fetch_stock_data()
        print(f"Total fetched raw records: {len(df):,}")
        inserted = populate_mongodb(df)
        print(f"Total inserted MongoDB documents: {inserted:,}")
    else:
        print(f"\n[Step 2/5] MongoDB already populated with {current_count:,} records (>= 100,000). Skipping download.")

    # 3. Executing 5 Financial Analysis Queries
    print("\n[Step 3/5] Executing 5 Financial Analysis Queries...")
    
    print("\n---> Query 1: 30-Day Moving Average & Price Trends (AAPL Sample)")
    q1 = analytics_engine.query_1_moving_averages("AAPL", limit=5)
    print(q1.to_string(index=False))
    
    print("\n---> Query 2: Top 5 Highest Single-Day Percentage Gainers")
    q2 = analytics_engine.query_2_highest_single_day_gains(top_n=5)
    print(q2[['ticker', 'date', 'close', 'daily_return']].to_string(index=False))
    
    print("\n---> Query 3: Top 5 Most Volatile Stocks (Daily Return Std Dev)")
    q3 = analytics_engine.query_3_volatility_ranking()
    if not q3.empty:
        print(q3.head(5).to_string(index=False))
        
    print("\n---> Query 4: Stock Daily Return Correlation Matrix (Sample)")
    q4 = analytics_engine.query_4_stock_correlation(["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"])
    print(q4.to_string())
    
    print("\n---> Query 5: Best & Worst Performing Stocks (Cumulative Returns)")
    _, top5, bot5 = analytics_engine.query_5_best_worst_performers()
    print("Top 5 Performers:\n", top5[['ticker', 'cumulative_return_pct']].to_string(index=False))
    print("Bottom 5 Performers:\n", bot5[['ticker', 'cumulative_return_pct']].to_string(index=False))

    # 4. Generating Visual Charts
    print("\n[Step 4/5] Generating Visual Performance Charts...")
    charts = visualizer.generate_all_charts()
    print(f"Generated {len(charts)} chart images in '{config.CHARTS_DIR}'")

    # 5. Building PDF Project Report
    print("\n[Step 5/5] Building PDF Project Report...")
    pdf_gen = PDFReportGenerator()
    pdf_file = pdf_gen.generate_pdf()
    print(f"PDF Project Report created at: {pdf_file}")

    print("\n" + "=" * 70)
    print(" SUCCESS! Pipeline executed cleanly and all outputs generated.")
    print("=" * 70)
    print(f" PDF Report: {pdf_file}")
    print(" Interactive Web Dashboard: Launch with 'streamlit run app.py'")
    print("=" * 70)

if __name__ == "__main__":
    main()
