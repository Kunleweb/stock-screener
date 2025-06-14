from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
import traceback
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = "JXIIGL9E44G1AXAT"

try:
    app = Flask(__name__)

    def get_stock_data(ticker, max_retries=3):
        for attempt in range(max_retries):
            try:
                print(f"\nAttempt {attempt + 1} to fetch data for {ticker}...")
                
                # Get quote data
                quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
                print("Fetching quote data...")
                quote_response = requests.get(quote_url)
                quote_data = quote_response.json()
                
                if "Error Message" in quote_data:
                    raise Exception(quote_data["Error Message"])
                
                if "Global Quote" not in quote_data:
                    raise Exception("No quote data available")
                
                quote = quote_data["Global Quote"]
                
                # Get company overview
                overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
                print("Fetching company overview...")
                overview_response = requests.get(overview_url)
                overview_data = overview_response.json()
                
                if "Error Message" in overview_data:
                    raise Exception(overview_data["Error Message"])
                
                # Calculate daily change
                current_price = float(quote["05. price"])
                prev_close = float(quote["08. previous close"])
                daily_change = ((current_price - prev_close) / prev_close) * 100
                
                # Format market cap
                market_cap = overview_data.get("MarketCapitalization", "N/A")
                if market_cap != "N/A":
                    market_cap = float(market_cap)
                    if market_cap >= 1e12:
                        market_cap = f"${market_cap/1e12:.2f}T"
                    elif market_cap >= 1e9:
                        market_cap = f"${market_cap/1e9:.2f}B"
                    elif market_cap >= 1e6:
                        market_cap = f"${market_cap/1e6:.2f}M"
                
                result = {
                    'ticker': ticker,
                    'current_price': round(current_price, 2),
                    'daily_change': round(daily_change, 2),
                    'market_cap': market_cap,
                    'pe_ratio': overview_data.get("PERatio", "N/A"),
                    'volume': f"{int(float(quote['06. volume'])):,}",
                    'high_52w': overview_data.get("52WeekHigh", "N/A"),
                    'low_52w': overview_data.get("52WeekLow", "N/A")
                }
                print(f"Successfully fetched data for {ticker}")
                return result
                
            except Exception as e:
                error_msg = f"Error fetching data for {ticker}: {str(e)}"
                print(error_msg)
                if attempt < max_retries - 1:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print(traceback.format_exc())
                    return {'error': error_msg}

    @app.route('/')
    def index():
        print("Index route accessed")
        return render_template('index.html')

    @app.route('/screen', methods=['POST'])
    def screen():
        print("\nScreen route accessed")
        tickers = request.form.get('tickers', '').split(',')
        tickers = [t.strip().upper() for t in tickers if t.strip()]
        print(f"Processing tickers: {tickers}")
        
        results = []
        for ticker in tickers:
            data = get_stock_data(ticker)
            if 'error' not in data:
                results.append(data)
            else:
                print(f"Error for {ticker}: {data['error']}")
        
        print(f"Returning {len(results)} results")
        return render_template('results.html', stocks=results)

    if __name__ == '__main__':
        print("Starting Flask application...")
        print("Templates directory:", app.template_folder)
        print("Static directory:", app.static_folder)
        app.run(host='127.0.0.1', port=8080, debug=True)

except Exception as e:
    print("An error occurred:")
    print(traceback.format_exc())
    print("\nPress Enter to exit...")
    input() 

application = app  