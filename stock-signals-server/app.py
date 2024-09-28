from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import yfinance as yf
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load stock symbols from CSV file
csv_file_path = os.path.join(os.getcwd(), "stocks.csv")  # Ensure correct path
stock_symbols_df = pd.read_csv(csv_file_path)
stock_symbol_list = stock_symbols_df['stock_symbol'].tolist()

def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

@app.route('/calculate', methods=['POST'])
def calculate_buy_signals():
    try:
        # Parse JSON data from the request
        data = request.json
        end_date = pd.to_datetime(data['endDate'])
        
        # Define start date as 200 days before the end date
        start_date = end_date - pd.DateOffset(days=200)
        
        # Data structure to store buy signals
        buy_signals = []

        # Loop over stock symbols from the CSV file
        for stock_symbol in stock_symbol_list:
            try:
                # Download stock data using yFinance
                stock_data = yf.download(stock_symbol, start=start_date, end=end_date)

                if stock_data.empty:
                    continue  # Skip if no data

                # Calculate 20-day and 50-day EMAs
                stock_data['20_EMA'] = calculate_ema(stock_data['Close'], 20)
                stock_data['50_EMA'] = calculate_ema(stock_data['Close'], 50)

                # Get the latest and previous EMA values
                tminus1_20ema = stock_data['20_EMA'].iloc[-1]
                tminus1_50ema = stock_data['50_EMA'].iloc[-1]
                tminus2_20ema = stock_data['20_EMA'].iloc[-2]
                tminus2_50ema = stock_data['50_EMA'].iloc[-2]

                # Check for buy signal (20 EMA crosses above 50 EMA)
                if tminus1_20ema > tminus1_50ema and tminus2_20ema < tminus2_50ema:
                    buy_price = stock_data['Close'].iloc[-1]
                    buy_signals.append({
                        "stockSymbol": stock_symbol,
                        "buyPrice": buy_price,
                        "date": str(end_date.date())
                    })

            except Exception as e:
                print(f"Error processing {stock_symbol}: {e}")

        # Return the list of buy signals as JSON
        return jsonify(buy_signals)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)

