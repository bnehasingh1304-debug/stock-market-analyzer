"""
Stock Market Tick Data Analyzer - Interactive Web Application
"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import config
from database import db_manager
from analytics import analytics_engine
from report_generator import PDFReportGenerator

# Auto-seed database if empty on page load
db_manager._auto_seed_if_empty()

st.set_page_config(
    page_title="Stock Market Tick Data Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application Header
st.title("📈 Stock Market Tick Data Analyzer")
st.markdown("##### Enterprise MongoDB Time-Series & High-Frequency Market Analytics System")

# Sidebar Controls
st.sidebar.header("⚙️ Controls & Navigation")
db_status = "💚 Live MongoDB Server" if not db_manager.is_mock else "⚡ MongoMock Embedded Engine"
st.sidebar.info(f"**Database Status:** {db_status}")

rec_count = db_manager.count_records()
st.sidebar.metric(label="Total Database Records", value=f"{rec_count:,}")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Ticker Selection")
selected_tickers = st.sidebar.multiselect(
    "Select Stocks for Comparison:",
    options=config.TICKERS,
    default=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📄 PDF Report Generator")
if st.sidebar.button("Generate & Download PDF Report"):
    with st.spinner("Building PDF Report..."):
        pdf_gen = PDFReportGenerator()
        pdf_path = pdf_gen.generate_pdf()
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.sidebar.download_button(
                label="📥 Download Project Report (PDF)",
                data=pdf_bytes,
                file_name="Stock_Market_Analyzer_Report.pdf",
                mime="application/pdf"
            )
            st.sidebar.success("Report generated successfully!")

# Main Application Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Interactive Price Comparison", 
    "🔍 5 Financial Analysis Queries", 
    "📊 Volatility Ranking Table", 
    "🗄️ Database & Schema Info"
])

# Tab 1: Interactive Stock Price Chart
with tab1:
    st.subheader("Stock Price Comparison Over Time")
    if selected_tickers:
        pivot_df = analytics_engine.get_time_series_comparison(selected_tickers)
        if not pivot_df.empty:
            fig = px.line(
                pivot_df, 
                x=pivot_df.index, 
                y=pivot_df.columns,
                labels={"value": "Closing Price (USD $)", "date": "Date", "variable": "Ticker"},
                title="Historical Closing Prices (USD)",
                template="plotly_white"
            )
            fig.update_layout(hovermode="x unified", legend_title_text="Ticker Symbols")
            st.plotly_chart(fig, use_container_width=True)

            # Single Ticker Moving Average Focus
            st.markdown("---")
            st.subheader("30-Day Moving Average Deep-Dive")
            focus_ticker = st.selectbox("Select ticker for Moving Average analysis:", selected_tickers)
            ma_df = analytics_engine.query_1_moving_averages(focus_ticker, limit=500)
            if not ma_df.empty:
                fig_ma = go.Figure()
                fig_ma.add_trace(go.Scatter(x=ma_df['date'], y=ma_df['close'], mode='lines', name='Closing Price', line=dict(color='#1f77b4', width=2)))
                fig_ma.add_trace(go.Scatter(x=ma_df['date'], y=ma_df['sma_30'], mode='lines', name='30-Day SMA', line=dict(color='#ff7f0e', width=2, dash='dash')))
                fig_ma.update_layout(title=f"{focus_ticker} Close Price vs 30-Day Simple Moving Average", xaxis_title="Date", yaxis_title="Price ($)", hovermode="x unified")
                st.plotly_chart(fig_ma, use_container_width=True)
        else:
            st.warning("No data found for selected tickers.")
    else:
        st.info("Please select at least one ticker in the sidebar.")

# Tab 2: 5 Financial Analysis Queries
with tab2:
    st.subheader("MongoDB Aggregation & Financial Analysis Queries")

    q_choice = st.radio(
        "Select Financial Analysis Query:",
        [
            "Query 1: 30-Day Moving Average & Price Trends",
            "Query 2: Highest Single-Day Percentage Gainers",
            "Query 3: Stock Volatility Ranking (Std Dev)",
            "Query 4: Stock Return Correlation Matrix",
            "Query 5: Best & Worst Performing Stocks (Cumulative Return)"
        ]
    )

    if q_choice.startswith("Query 1"):
        st.markdown("### Query 1: 30-Day Moving Average")
        t_sel = st.selectbox("Select Ticker for Query 1:", config.TICKERS[:15], index=0)
        res_df = analytics_engine.query_1_moving_averages(t_sel, limit=50)
        st.dataframe(res_df, use_container_width=True)

    elif q_choice.startswith("Query 2"):
        st.markdown("### Query 2: Highest Single-Day Percentage Gainers")
        top_n = st.slider("Top N Gainers:", 5, 50, 10)
        res_df = analytics_engine.query_2_highest_single_day_gains(top_n=top_n)
        st.dataframe(res_df, use_container_width=True)

    elif q_choice.startswith("Query 3"):
        st.markdown("### Query 3: Stock Volatility Ranking")
        res_df = analytics_engine.query_3_volatility_ranking()
        st.dataframe(res_df, use_container_width=True)

    elif q_choice.startswith("Query 4"):
        st.markdown("### Query 4: Stock Correlation Matrix")
        corr_tickers = st.multiselect("Select tickers for correlation matrix:", config.TICKERS[:20], default=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"])
        if corr_tickers:
            corr_df = analytics_engine.query_4_stock_correlation(corr_tickers)
            st.dataframe(corr_df.style.background_gradient(cmap='coolwarm', axis=None), use_container_width=True)

    elif q_choice.startswith("Query 5"):
        st.markdown("### Query 5: Best & Worst Performing Stocks")
        all_df, top_5, bot_5 = analytics_engine.query_5_best_worst_performers()
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 🟢 Top 5 Best Performers")
            st.dataframe(top_5, use_container_width=True)
        with col_b:
            st.markdown("#### 🔴 Top 5 Worst Performers")
            st.dataframe(bot_5, use_container_width=True)

# Tab 3: Volatility Ranking Table
with tab3:
    st.subheader("Stock Risk & Volatility Metrics")
    st.markdown("Ranks stocks based on standard deviation of daily percentage returns.")
    vol_df = analytics_engine.query_3_volatility_ranking()
    if not vol_df.empty:
        st.dataframe(
            vol_df.style.format({
                "volatility_std_dev": "{:.2f}%",
                "avg_return": "{:.2f}%",
                "min_return": "{:.2f}%",
                "max_return": "{:.2f}%"
            }),
            use_container_width=True
        )

# Tab 4: Database & Schema Info
with tab4:
    st.subheader("MongoDB Database & Collection Schema")
    st.markdown(f"**Database Name:** `{config.DB_NAME}`")
    st.markdown(f"**Collection Name:** `{config.COLLECTION_NAME}`")
    st.markdown(f"**Document Count:** `{rec_count:,}` records")
    st.markdown(f"**Database Mode:** `{'Live MongoDB Cluster' if not db_manager.is_mock else 'MongoMock Embedded Engine'}`")

    st.markdown("---")
    st.markdown("#### Sample Collection Document Schema")
    sample_doc = db_manager.get_collection().find_one({}, {"_id": 0})
    if sample_doc:
        st.json(sample_doc)

st.markdown("---")
st.caption("Stock Market Tick Data Analyzer | Built with MongoDB, Python, yfinance, Streamlit & ReportLab")
