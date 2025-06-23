import logging
from decimal import Decimal, ROUND_DOWN
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger(__name__)

def get_symbol_precision(client, symbol: str) -> dict:
    
    # Fetches the precision rules for a given symbol from Binance exchange info.
    
    try:
        exchange_info = client.futures_exchange_info()
        for s in exchange_info['symbols']:
            if s['symbol'] == symbol:
                price_precision = s['pricePrecision']
                quantity_precision = s['quantityPrecision']
                logger.info(f"Fetched precision for {symbol}: "
                            f"Price Precision = {price_precision}, "
                            f"Quantity Precision = {quantity_precision}")
                return {
                    'price_precision': price_precision,
                    'quantity_precision': quantity_precision
                }
        logger.warning(f"Symbol '{symbol}' not found in exchange info.")
        return {}
    except (BinanceAPIException, BinanceRequestException) as e:
        logger.error(f"Binance API/Request Exception fetching symbol precision for {symbol}: {e}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred fetching symbol precision for {symbol}: {e}")
        return {}
    


def format_quantity(quantity: float, precision: int) -> str:

    # Formats a quantity to the specified decimal precision, rounding down.
    if precision < 0:
        factor = 10**abs(precision)
        return str(int(quantity // factor * factor))

    fmt_str = '0.' + '0' * precision
    return str(Decimal(str(quantity)).quantize(Decimal(fmt_str), rounding=ROUND_DOWN))

def format_price(price: float, precision: int) -> str:

    # Formats a price to the specified decimal precision, rounding down.
    if precision < 0:
        factor = 10**abs(precision)
        return str(int(price // factor * factor))

    fmt_str = '0.' + '0' * precision
    return str(Decimal(str(price)).quantize(Decimal(fmt_str), rounding=ROUND_DOWN))

def get_binance_server_time(client) -> int:
    
    # Fetches the current Binance server time in milliseconds, useful for ensuring accurate timestamps in signed API requests.

    try:
        server_time = client.futures_time()['serverTime']
        logger.info(f"Fetched Binance server time: {server_time} ms")
        return server_time
    except (BinanceAPIException, BinanceRequestException) as e:
        logger.error(f"Binance API/Request Exception fetching server time: {e}")
        return 0
    except Exception as e:
        logger.error(f"An unexpected error occurred fetching server time: {e}")
        return 0