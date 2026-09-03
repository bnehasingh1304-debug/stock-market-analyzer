"""
Stock Market Tick Data Analyzer - Standard Flask & HTML Web Server
"""
import os
from flask import Flask, render_template, jsonify, request, send_from_directory
import config
from database import db_manager
from analytics import analytics_engine

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    db_manager._auto_seed_if_empty()
    record_count = db_manager.count_records()
    return render_template("index.html", record_count=record_count, tickers=config.TICKERS[:15])

@app.route("/api/comparison")
def api_comparison():
    tickers = request.args.get("tickers", "AAPL,MSFT,GOOGL,NVDA,TSLA").split(",")
    df = analytics_engine.get_time_series_comparison(tickers)
    if df.empty:
        return jsonify({})
    df_reset = df.reset_index()
    df_reset['date'] = df_reset['date'].astype(str)
    return jsonify(df_reset.to_dict(orient="list"))

@app.route("/api/volatility")
def api_volatility():
    df = analytics_engine.query_3_volatility_ranking()
    if df.empty:
        return jsonify([])
    return jsonify(df.head(15).to_dict(orient="records"))

@app.route("/api/gains")
def api_gains():
    df = analytics_engine.query_2_highest_single_day_gains(top_n=10)
    if df.empty:
        return jsonify([])
    df['date'] = df['date'].astype(str)
    return jsonify(df.to_dict(orient="records"))

@app.route("/reports/<path:filename>")
def serve_report(filename):
    return send_from_directory(config.REPORTS_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
