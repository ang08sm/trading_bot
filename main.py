import os 
import logging
import sys

from bot.basic_bot import BasicBot
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET, DEFAULT_SYMBOL, DEFAULT_QUANTITY
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def get_user_input(prompt: str, type_func=str, validator=None, error_message="Invalid input. Please try again."):
    """
    Gets user input with optional type conversion and validation.

    Args:
        prompt (str): Message to display to the user.
        type_func (function): Function to convert input type (e.g., int, float).
        validator (function, optional): A function that takes the input and returns True if valid, False otherwise.
        error_message (str): Message to display if validation fails.

    Returns:
        The validated input in the desired type.
    """
    while True:
        user_input = input(prompt).strip()
        try:
            value = type_func(user_input)
            if validator and not validator(value):
                logger.warning(f"User input validation failed: '{user_input}'. {error_message}")
                print(f"Error: {error_message}")
                continue
            return value
        except ValueError:
            logger.warning(f"User entered invalid type: '{user_input}'. Expected {type_func.__name__}.")
            print(f"Error: Invalid input. Please enter a valid {type_func.__name__}.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during input: {e}")
            print("An unexpected error occurred. Please try again.")

def run_cli():
    """
    Runs the command-line interface for the trading bot.
    """
    logger.info("Starting Binance Futures Trading Bot CLI...")

    # Initialize the bot
    bot = BasicBot(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET, testnet=True)

    if not bot.client:
        logger.critical("Bot failed to connect to Binance. Exiting CLI.")
        print("\nFailed to connect to Binance Testnet. Please check your API keys and internet connection.")
        print("See logs/trading_bot.log for more details.")
        sys.exit(1)

    while True:
        print("\n--- Trading Bot Menu ---")
        print("1. Place Market Order")
        print("2. Place Limit Order")
        print("3. Get Account Info")
        print("4. Get Market Price")
        print("5. Exit")
        print("------------------------")

        choice = get_user_input("Enter your choice (1-5): ", type_func=int,
                                validator=lambda x: 1 <= x <= 5,
                                error_message="Choice must be between 1 and 5.")

        if choice == 1: # Place Market Order
            print("\n--- Place Market Order ---")
            symbol = get_user_input(f"Enter trading symbol (e.g., {DEFAULT_SYMBOL}): ",
                                    validator=lambda s: len(s) > 0,
                                    error_message="Symbol cannot be empty.").upper()
            side = get_user_input("Enter order side (BUY/SELL): ",
                                validator=lambda s: s.upper() in ["BUY", "SELL"],
                                error_message="Side must be 'BUY' or 'SELL'.").upper()
            quantity = get_user_input(f"Enter quantity (e.g., {DEFAULT_QUANTITY}): ", type_func=float,
                                    validator=lambda q: q > 0,
                                    error_message="Quantity must be a positive number.")

            print(f"\nAttempting to place MARKET {side} order for {quantity} {symbol}...")
            order_response = bot.place_market_order(symbol, side, quantity)
            if order_response:
                print("\nMARKET Order Placed Successfully!")
                print(f"Order ID: {order_response.get('orderId')}")
                print(f"Symbol: {order_response.get('symbol')}")
                print(f"Side: {order_response.get('side')}")
                print(f"Type: {order_response.get('type')}")
                print(f"Status: {order_response.get('status')}")
                if order_response.get('fills'):
                    print(f"Executed Price: {order_response['fills'][0].get('price')}")
            else:
                print("\nFailed to place MARKET order. Check logs for details.")

        elif choice == 2: # Place Limit Order
            print("\n--- Place Limit Order ---")
            symbol = get_user_input(f"Enter trading symbol (e.g., {DEFAULT_SYMBOL}): ",
                                    validator=lambda s: len(s) > 0,
                                    error_message="Symbol cannot be empty.").upper()
            side = get_user_input("Enter order side (BUY/SELL): ",
                                  validator=lambda s: s.upper() in ["BUY", "SELL"],
                                  error_message="Side must be 'BUY' or 'SELL'.").upper()
            quantity = get_user_input(f"Enter quantity (e.g., {DEFAULT_QUANTITY}): ", type_func=float,
                                      validator=lambda q: q > 0,
                                      error_message="Quantity must be a positive number.")
            price = get_user_input("Enter limit price: ", type_func=float,
                                   validator=lambda p: p > 0,
                                   error_message="Price must be a positive number.")

            print(f"\nAttempting to place LIMIT {side} order for {quantity} {symbol} at {price}...")
            order_response = bot.place_limit_order(symbol, side, quantity, price)
            if order_response:
                print("\nLIMIT Order Placed Successfully!")
                print(f"Order ID: {order_response.get('orderId')}")
                print(f"Symbol: {order_response.get('symbol')}")
                print(f"Side: {order_response.get('side')}")
                print(f"Type: {order_response.get('type')}")
                print(f"Price: {order_response.get('price')}")
                print(f"Status: {order_response.get('status')}")
            else:
                print("\nFailed to place LIMIT order. Check logs for details.")

        elif choice == 3: # Get Account Info
            print("\n--- Account Information ---")
            account_info = bot.get_account_info()
            if account_info:
                print("\nAccount Details:")
                for asset in account_info.get('assets', []):
                    print(f"  Asset: {asset.get('asset')}")
                    print(f"    Wallet Balance: {asset.get('walletBalance')}")
                    print(f"    Available Balance: {asset.get('availableBalance')}")
                    print(f"    Margin Balance: {asset.get('marginBalance')}")
                print(f"  Total Initial Margin: {account_info.get('totalInitialMargin')}")
                print(f"  Total Unrealized Profit: {account_info.get('totalUnrealizedProfit')}")
            else:
                print("\nFailed to retrieve account information. Check logs for details.")

        elif choice == 4: # Get Market Price
            print("\n--- Get Market Price ---")
            symbol = get_user_input(f"Enter trading symbol (e.g., {DEFAULT_SYMBOL}): ",
                                    validator=lambda s: len(s) > 0,
                                    error_message="Symbol cannot be empty.").upper()
            market_price = bot.get_market_price(symbol)
            if market_price > 0:
                print(f"\nCurrent Market Price for {symbol}: {market_price}")
            else:
                print(f"\nFailed to retrieve market price for {symbol}. Check logs for details.")

        elif choice == 5:
            print("Exiting Trading Bot :)")
            logger.info("Trading Bot CLI exited")
            break

if __name__ == "__main__":
    run_cli()