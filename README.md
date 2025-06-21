# Simplified Binance Futures Trading Bot

This project implements a basic command-line interface (CLI) trading bot designed to interact with the **Binance Futures Testnet (USDT-M)**. It allows users to securely place market and limit orders, retrieve account information, and get real-time market prices, all while ensuring robust logging and error handling.

## 🚀 Features

* **Binance Futures Testnet Integration:** Connects to Binance's test environment for safe experimentation.
* **Order Placement:**
    * Place **Market Orders** (BUY/SELL)
    * Place **Limit Orders** (BUY/SELL)
* **Account Information:** Retrieve and display your Binance Futures Testnet account balances and margin details.
* **Market Data:** Fetch current market prices for specified symbols.
* **Command-Line Interface (CLI):** User-friendly interactive menu for bot operations.
* **Robust Logging:** Detailed logs of API requests, responses, and errors saved to a file (`logs/trading_bot.log`) and displayed in the console.
* **Error Handling:** Graceful handling of common API exceptions and input validation.
* **Secure API Key Management:** Uses environment variables (`.env`) to keep sensitive API credentials out of the codebase.
* **Precision Handling:** Automatically formats quantities and prices according to Binance's symbol-specific precision rules.