import os
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)
load_dotenv()

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
BINANCE_TESTNET_BASE_URL = "https://testnet.binancefuture.com"

if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    logger.error("BINANCE_API_KEY or BINANCE_API_SECRET not found in environment variables.")
    logger.info("Please setup your API Credentials")

# Default Trading Parameters
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_QUANTITY = 0.001