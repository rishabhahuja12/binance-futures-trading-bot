"""
Binance Futures Testnet client wrapper.

Handles connection setup and exposes wrapper methods for futures endpoints.
Loads credentials from .env. Contains NO business logic.
"""

import os
import logging

from binance.client import Client
from dotenv import load_dotenv

logger = logging.getLogger("trading_bot")


class BinanceTestnetClient:
    """Wrapper around python-binance for Binance Futures Testnet."""

    def __init__(self):
        """Initialize client. Loads API_KEY/API_SECRET from .env.

        Raises:
            ValueError: If credentials are missing.
        """
        load_dotenv()

        api_key = os.getenv("API_KEY")
        api_secret = os.getenv("API_SECRET")

        if not api_key or not api_secret:
            raise ValueError(
                "API_KEY and API_SECRET must be set in the .env file."
            )

        self._client = Client(api_key, api_secret, testnet=True)
        logger.info("Binance Futures Testnet client initialized")

    def futures_create_order(self, **params):
        """Place a futures order. Thin wrapper — forwards to python-binance.

        Args:
            **params: Order parameters (symbol, side, type, quantity, etc.)

        Returns:
            dict: Raw API response from Binance.
        """
        logger.info("Sending futures order request: %s", params)
        response = self._client.futures_create_order(**params)
        logger.info("Futures order response: %s", response)
        return response
