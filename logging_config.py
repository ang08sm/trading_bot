import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging() :
    """
    Sets up the logging configuration for the application.
    Logs messages to a file (rotating) and to the console.
    """

    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, 'trading_bot.log')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.getLogger('binance.client').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    logger.info("Logging configured successfully")