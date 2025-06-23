import logging

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceResolutionError
from config.settings import BINANCE_TESTNET_BASE_URL
from bot.binance_utils import get_symbol_precision, format_quantity, format_price, get_binance_server_time

logger = logging.getLogger(__name__)

class BasicBot:
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.client = None
        self._connect_client()
        self.symbol_precisions = {} 

    def _connect_client(self):
        
        if not self.api_key or not self.api_secret:
            logger.error("API Key or Secret Key is missing. Cannot connect to Binance.")
            return

        try:
            if self.testnet:
                self.client = Client(
                    self.api_key,
                    self.api_secret,
                    base_url=BINANCE_TESTNET_BASE_URL
                )
            else:
                self.client = Client(self.api_key, self.api_secret)

            
            self.client.futures_ping()
            logger.info("Successfully connected to Binance Futures Testnet.")

            server_time = get_binance_server_time(self.client)
            if server_time:
                logger.info(f"Binance Server Time: {server_time}")

            logger.info(f"Account Information: {self.get_account_info()}") 
        except BinanceAPIException as e:
            logger.error(f"Binance API Exception during connection: {e.code} - {e.message}")
            self.client = None 

        except BinanceRequestException as e:
            logger.error(f"Binance Request Exception during connection: {e}")
            self.client = None

        except Exception as e:
            logger.error(f"An unexpected error occurred during connection: {e}")
            self.client = None

    def _get_or_fetch_precision(self, symbol: str):
        
        if symbol not in self.symbol_precisions:
            if self.client:
                precisions = get_symbol_precision(self.client, symbol)
                if precisions:
                    self.symbol_precisions[symbol] = precisions
                else:
                    logger.warning(f"Could not retrieve precision for {symbol}. "
                                f"Orders might fail due to incorrect formatting.")
            else:
                logger.error("Binance client not connected. Cannot fetch symbol precision.")
                return None
        return self.symbol_precisions.get(symbol)

    def get_account_info(self) -> dict:
        
        if not self.client:
            logger.error("Binance client not connected. Cannot get account info.")
            return {}
        try:
            info = self.client.futures_account()
            logger.info("Successfully retrieved futures account information.")
            for asset in info['assets']:
                logger.info(f"Asset: {asset['asset']}, Wallet Balance: {asset['walletBalance']}, "
                            f"Cross Wallet Balance: {asset['crossWalletBalance']}")
            logger.info(f"Total Initial Margin: {info.get('totalInitialMargin')}")
            return info
        except BinanceAPIException as e:
            logger.error(f"Binance API Exception getting account info: {e.code} - {e.message}")
        except BinanceRequestException as e:
            logger.error(f"Binance Request Exception getting account info: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred getting account info: {e}")
        return {}

    def get_market_price(self, symbol: str) -> float:
    
        if not self.client:
            logger.error("Binance client not connected. Cannot get market price.")
            return 0.0
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            logger.info(f"Current market price for {symbol}: {price}")
            return price
        except BinanceAPIException as e:
            logger.error(f"Binance API Exception getting market price for {symbol}: {e.code} - {e.message}")
        except BinanceRequestException as e:
            logger.error(f"Binance Request Exception getting market price for {symbol}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred getting market price for {symbol}: {e}")
        return 0.0

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        
        if not self.client:
            logger.error("Binance client not connected. Cannot place order.")
            return None

        if order_type not in ["MARKET", "LIMIT"]:
            logger.error(f"Invalid order type: {order_type}. Must be 'MARKET' or 'LIMIT'.")
            return None
        if side not in ["BUY", "SELL"]:
            logger.error(f"Invalid side: {side}. Must be 'BUY' or 'SELL'.")
            return None

        precisions = self._get_or_fetch_precision(symbol)
        if not precisions:
            logger.error(f"Failed to get precision for {symbol}. Cannot place order.")
            return None

        quantity_precision = precisions['quantity_precision']
        price_precision = precisions['price_precision']

        formatted_quantity = format_quantity(quantity, quantity_precision)
        logger.info(f"Original quantity: {quantity}, Formatted quantity: {formatted_quantity}")

        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': formatted_quantity,
        }

        if order_type == Client.ORDER_TYPE_LIMIT:
            if price is None:
                logger.error("Price is required for LIMIT orders.")
                return None
            formatted_price = format_price(price, price_precision)
            params['price'] = formatted_price
            params['timeInForce'] = 'GTC'
            logger.info(f"Original price: {price}, Formatted price: {formatted_price}")

        logger.info(f"Attempting to place {order_type} order: {params}")

        try:
            order = self.client.futures_create_order(**params)
            logger.info(f"Order placed successfully: {order}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Binance API Exception placing order: {e.code} - {e.message} (params: {params})")
        except BinanceRequestException as e:
            logger.error(f"Binance Request Exception placing order: {e} (params: {params})")
        except BinanceResolutionError as e:
            logger.error(f"Binance Resolution Error (network issue?): {e} (params: {params})")
        except Exception as e:
            logger.error(f"An unexpected error occurred placing order: {e} (params: {params})")
        return None

    def place_market_order(self, symbol: str, side: str, quantity: float):
        
        logger.info(f"Placing MARKET {side} order for {quantity}{symbol}")
        return self.place_order(symbol, side, Client.ORDER_TYPE_MARKET, quantity)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float):
        
        logger.info(f"Placing LIMIT {side} order for {quantity}{symbol} at {price}")
        return self.place_order(symbol, side, Client.ORDER_TYPE_LIMIT, quantity, price)