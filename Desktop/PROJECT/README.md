# Stock Screener

A Flask-based web application that allows users to screen and analyze stock data using the Alpha Vantage API.

## Features

- Real-time stock data retrieval
- Multiple stock ticker support
- Key financial metrics display:
  - Current price
  - Daily change
  - Market cap
  - P/E ratio
  - Volume
  - 52-week high/low

## Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd stock-screener
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
FLASK_ENV=production
```

5. Run the application:
```bash
python app.py
```

## Environment Variables

- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key
- `FLASK_ENV`: Set to 'production' for production deployment

## Dependencies

- Flask==3.0.2
- requests==2.31.0
- pandas==2.2.1
- python-dotenv==1.0.1

## Project Structure

```
stock_screener/
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
├── .env               # Environment variables (not in git)
├── .gitignore         # Git ignore file
├── templates/         # HTML templates
│   ├── index.html     # Home page
│   ├── results.html   # Results page
│   ├── 404.html       # Not found page
│   └── 500.html       # Server error page
└── README.md          # This file
```

## License

MIT License 