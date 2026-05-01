"""Tests for bot.validators module."""

import pytest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_order_input,
)


# ── validate_symbol ──────────────────────────────────────────────

class TestValidateSymbol:
    def test_valid_symbol(self):
        assert validate_symbol("BTCUSDT") == "BTCUSDT"

    def test_lowercase_auto_uppercased(self):
        assert validate_symbol("btcusdt") == "BTCUSDT"

    def test_mixed_case(self):
        assert validate_symbol("BtcUsDt") == "BTCUSDT"

    def test_whitespace_trimmed(self):
        assert validate_symbol("  ETHUSDT  ") == "ETHUSDT"

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            validate_symbol("")

    def test_none_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            validate_symbol(None)

    def test_numeric_symbol_raises(self):
        with pytest.raises(ValueError, match="Invalid symbol"):
            validate_symbol("123")

    def test_special_chars_raises(self):
        with pytest.raises(ValueError, match="Invalid symbol"):
            validate_symbol("BTC-USDT")

    def test_single_char_raises(self):
        with pytest.raises(ValueError, match="Invalid symbol"):
            validate_symbol("A")


# ── validate_side ────────────────────────────────────────────────

class TestValidateSide:
    def test_buy(self):
        assert validate_side("BUY") == "BUY"

    def test_sell(self):
        assert validate_side("SELL") == "SELL"

    def test_lowercase_buy(self):
        assert validate_side("buy") == "BUY"

    def test_invalid_side(self):
        with pytest.raises(ValueError, match="Invalid side"):
            validate_side("HOLD")

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            validate_side("")


# ── validate_order_type ──────────────────────────────────────────

class TestValidateOrderType:
    def test_market(self):
        assert validate_order_type("MARKET") == "MARKET"

    def test_limit(self):
        assert validate_order_type("LIMIT") == "LIMIT"

    def test_lowercase(self):
        assert validate_order_type("market") == "MARKET"

    def test_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid order type"):
            validate_order_type("STOP")

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            validate_order_type("")


# ── validate_quantity ────────────────────────────────────────────

class TestValidateQuantity:
    def test_positive_float(self):
        assert validate_quantity(0.01) == 0.01

    def test_positive_int(self):
        assert validate_quantity(1) == 1.0

    def test_string_number(self):
        assert validate_quantity("0.5") == 0.5

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            validate_quantity(0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="positive"):
            validate_quantity(-1)

    def test_non_numeric_raises(self):
        with pytest.raises(ValueError, match="valid number"):
            validate_quantity("abc")

    def test_none_raises(self):
        with pytest.raises(ValueError, match="valid number"):
            validate_quantity(None)


# ── validate_price ───────────────────────────────────────────────

class TestValidatePrice:
    def test_limit_valid_price(self):
        assert validate_price(60000.0, "LIMIT") == 60000.0

    def test_limit_string_price(self):
        assert validate_price("3000", "LIMIT") == 3000.0

    def test_limit_missing_price_raises(self):
        with pytest.raises(ValueError, match="required for LIMIT"):
            validate_price(None, "LIMIT")

    def test_limit_zero_price_raises(self):
        with pytest.raises(ValueError, match="positive"):
            validate_price(0, "LIMIT")

    def test_limit_negative_price_raises(self):
        with pytest.raises(ValueError, match="positive"):
            validate_price(-100, "LIMIT")

    def test_market_no_price(self):
        assert validate_price(None, "MARKET") is None

    def test_market_with_price_raises(self):
        with pytest.raises(ValueError, match="must not be provided"):
            validate_price(5000, "MARKET")


# ── validate_order_input (integration) ───────────────────────────

class TestValidateOrderInput:
    def test_valid_market_order(self):
        result = validate_order_input("BTCUSDT", "BUY", "MARKET", 0.01)
        assert result["symbol"] == "BTCUSDT"
        assert result["side"] == "BUY"
        assert result["order_type"] == "MARKET"
        assert result["quantity"] == 0.01
        assert "price" not in result

    def test_valid_limit_order(self):
        result = validate_order_input(
            "ETHUSDT", "SELL", "LIMIT", 0.1, price=3000
        )
        assert result["symbol"] == "ETHUSDT"
        assert result["side"] == "SELL"
        assert result["order_type"] == "LIMIT"
        assert result["quantity"] == 0.1
        assert result["price"] == 3000.0

    def test_limit_without_price_raises(self):
        with pytest.raises(ValueError, match="required for LIMIT"):
            validate_order_input("BTCUSDT", "BUY", "LIMIT", 0.01)

    def test_market_with_price_raises(self):
        with pytest.raises(ValueError, match="must not be provided"):
            validate_order_input(
                "BTCUSDT", "BUY", "MARKET", 0.01, price=5000
            )

    def test_invalid_symbol_propagates(self):
        with pytest.raises(ValueError):
            validate_order_input("123", "BUY", "MARKET", 0.01)
