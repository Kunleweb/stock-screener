from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
import traceback
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('./templates/config.env')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_screener.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Get API key from environment variable
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
if not ALPHA_VANTAGE_API_KEY:
    logger.error("ALPHA_VANTAGE_API_KEY not found in environment variables")
    raise ValueError("ALPHA_VANTAGE_API_KEY environment variable is required")

app = Flask(__name__)

def get_stock_data(ticker, max_retries=3):
    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1} to fetch data for {ticker}")
            
            # Get quote data
            quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            logger.debug(f"Fetching quote data from: {quote_url}")
            quote_response = requests.get(quote_url, timeout=10)
            quote_response.raise_for_status()
            quote_data = quote_response.json()
            logger.debug(f"Quote data response: {quote_data}")
            
            if "Error Message" in quote_data:
                raise Exception(quote_data["Error Message"])
            
            if "Global Quote" not in quote_data:
                raise Exception("No quote data available")
            
            quote = quote_data["Global Quote"]
            
            # Get company overview
            overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            logger.debug(f"Fetching company overview from: {overview_url}")
            overview_response = requests.get(overview_url, timeout=10)
            overview_response.raise_for_status()
            overview_data = overview_response.json()
            logger.debug(f"Overview data response: {overview_data}")
            
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
            logger.info(f"Successfully fetched data for {ticker}: {result}")
            return result
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout while fetching data for {ticker}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                return {'error': f"Timeout while fetching data for {ticker}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {ticker}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                return {'error': f"Request error for {ticker}: {str(e)}"}
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                return {'error': f"Error fetching data for {ticker}: {str(e)}"}

@app.route('/')
def index():
    logger.info("Index route accessed")
    return render_template('index.html')

@app.route('/screen', methods=['POST'])
def screen():
    logger.info("Screen route accessed")
    tickers = request.form.get('tickers', '').split(',')
    tickers = [t.strip().upper() for t in tickers if t.strip()]
    logger.info(f"Processing tickers: {tickers}")
    
    if not tickers:
        return render_template('index.html', error="Please enter at least one ticker symbol")
    
    results = []
    for ticker in tickers:
        data = get_stock_data(ticker)
        if 'error' not in data:
            results.append(data)
        else:
            logger.error(f"Error for {ticker}: {data['error']}")
    
    logger.info(f"Returning {len(results)} results: {results}")
    return render_template('results.html', stocks=results)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
else:
    # This is for PythonAnywhere
    application = app  