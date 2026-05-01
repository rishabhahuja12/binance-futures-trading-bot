"""Tests for bot.orders module.

Uses unittest.mock to mock API responses — never hits real API in unit tests.
"""

import pytest
from unittest.mock import MagicMock
from binance.exceptions import BinanceAPIException

from bot.orders import build_order_params, parse_order_response, place_order


# ── build_order_params ───────────────────────────────────────────

class TestBuildOrderParams:
    def test_market_order_params(self):
        validated = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 0.01,
        }
        params = build_order_params(validated)
        assert params == {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quantity": 0.01,
        }
        assert "price" not in params
        assert "timeInForce" not in params

    def test_limit_order_params(self):
        validated = {
            "symbol": "ETHUSDT",
            "side": "SELL",
            "order_type": "LIMIT",
            "quantity": 0.1,
            "price": 3000.0,
        }
        params = build_order_params(validated)
        assert params == {
            "symbol": "ETHUSDT",
            "side": "SELL",
            "type": "LIMIT",
            "quantity": 0.1,
            "price": 3000.0,
            "timeInForce": "GTC",
        }


# ── parse_order_response ────────────────────────────────────────

class TestParseOrderResponse:
    def test_full_response(self):
        response = {
            "orderId": 12345,
            "status": "FILLED",
            "executedQty": "0.01",
            "avgPrice": "60000.00",
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "origQty": "0.01",
        }
        parsed = parse_order_response(response)
        assert parsed["orderId"] == 12345
        assert parsed["status"] == "FILLED"
        assert parsed["executedQty"] == "0.01"
        assert parsed["avgPrice"] == "60000.00"

    def test_partial_response(self):
        response = {"orderId": 999, "status": "NEW"}
        parsed = parse_order_response(response)
        assert parsed["orderId"] == 999
        assert "executedQty" not in parsed

    def test_missing_order_id_logs_warning(self):
        response = {"status": "NEW"}
        parsed = parse_order_response(response)
        assert "orderId" not in parsed

    def test_non_dict_raises(self):
        with pytest.raises(ValueError, match="Unexpected response"):
            parse_order_response("not a dict")

    def test_none_raises(self):
        with pytest.raises(ValueError, match="Unexpected response"):
            parse_order_response(None)


# ── place_order (mocked client) ─────────────────────────────────

class TestPlaceOrder:
    def _make_mock_client(self, response):
        """Create a mock client that returns the given response."""
        client = MagicMock()
        client.futures_create_order.return_value = response
        return client

    def test_successful_market_order(self):
        mock_response = {
            "orderId": 111,
            "status": "FILLED",
            "executedQty": "0.01",
            "avgPrice": "60500.00",
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
        }
        client = self._make_mock_client(mock_response)
        validated = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 0.01,
        }

        result = place_order(client, validated)

        assert result["orderId"] == 111
        assert result["status"] == "FILLED"
        client.futures_create_order.assert_called_once_with(
            symbol="BTCUSDT", side="BUY", type="MARKET", quantity=0.01,
        )

    def test_successful_limit_order(self):
        mock_response = {
            "orderId": 222,
            "status": "NEW",
            "executedQty": "0.00",
            "avgPrice": "0.00",
            "symbol": "ETHUSDT",
            "side": "SELL",
            "type": "LIMIT",
        }
        client = self._make_mock_client(mock_response)
        validated = {
            "symbol": "ETHUSDT",
            "side": "SELL",
            "order_type": "LIMIT",
            "quantity": 0.1,
            "price": 3000.0,
        }

        result = place_order(client, validated)

        assert result["orderId"] == 222
        assert result["status"] == "NEW"
        client.futures_create_order.assert_called_once_with(
            symbol="ETHUSDT", side="SELL", type="LIMIT",
            quantity=0.1, price=3000.0, timeInForce="GTC",
        )

    def test_api_error_propagates(self):
        client = MagicMock()
        error_text = '{"code":-1121,"msg":"Invalid symbol."}'
        mock_response = MagicMock(status_code=400, text=error_text)
        client.futures_create_order.side_effect = BinanceAPIException(
            mock_response, 400, error_text
        )
        validated = {
            "symbol": "INVALID",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 0.01,
        }

        with pytest.raises(BinanceAPIException):
            place_order(client, validated)

    def test_connection_error_propagates(self):
        client = MagicMock()
        client.futures_create_order.side_effect = ConnectionError(
            "No internet"
        )
        validated = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 0.01,
        }

        with pytest.raises(ConnectionError):
            place_order(client, validated)
