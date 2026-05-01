"""
Input validation for trading bot CLI.

Validates symbol, side, order type, quantity, and price.
Single-responsibility: validation only, no API calls.
"""

import re
import logging

logger = logging.getLogger("trading_bot")

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT")


def validate_symbol(symbol):
    """Validate trading symbol format.

    Args:
        symbol: Trading pair (e.g., BTCUSDT).

    Returns:
        str: Uppercased, trimmed symbol.

    Raises:
        ValueError: If symbol is invalid.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string")

    symbol = symbol.upper().strip()

    if not re.match(r"^[A-Z]{2,20}$", symbol):
        raise ValueError(
            f"Invalid symbol format: '{symbol}'. "
            "Must contain only letters (e.g., BTCUSDT)"
        )

    return symbol


def validate_side(side):
    """Validate order side (BUY or SELL).

    Returns:
        str: Validated, uppercased side.

    Raises:
        ValueError: If side is invalid.
    """
    if not side or not isinstance(side, str):
        raise ValueError("Side must be a non-empty string")

    side = side.upper().strip()

    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side: '{side}'. Must be: {', '.join(VALID_SIDES)}"
        )

    return side


def validate_order_type(order_type):
    """Validate order type (MARKET or LIMIT).

    Returns:
        str: Validated, uppercased order type.

    Raises:
        ValueError: If order type is invalid.
    """
    if not order_type or not isinstance(order_type, str):
        raise ValueError("Order type must be a non-empty string")

    order_type = order_type.upper().strip()

    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type: '{order_type}'. "
            f"Must be: {', '.join(VALID_ORDER_TYPES)}"
        )

    return order_type


def validate_quantity(quantity):
    """Validate order quantity (must be positive float).

    Returns:
        float: Validated quantity.

    Raises:
        ValueError: If quantity is invalid or not positive.
    """
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(
            f"Quantity must be a valid number, got: '{quantity}'"
        )

    if quantity <= 0:
        raise ValueError(f"Quantity must be positive, got: {quantity}")

    return quantity


def validate_price(price, order_type):
    """Validate price based on order type.

    Price is required for LIMIT and rejected for MARKET.

    Returns:
        float or None: Validated price, or None for MARKET.

    Raises:
        ValueError: If price rules are violated.
    """
    if order_type == "MARKET":
        if price is not None:
            raise ValueError(
                "Price must not be provided for MARKET orders"
            )
        return None

    # LIMIT — price is required
    if price is None:
        raise ValueError("Price is required for LIMIT orders")

    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Price must be a valid number, got: '{price}'")

    if price <= 0:
        raise ValueError(f"Price must be positive, got: {price}")

    return price


def validate_order_input(symbol, side, order_type, quantity, price=None):
    """Validate all order inputs and return a validated dict.

    Args:
        symbol: Trading pair symbol.
        side: BUY or SELL.
        order_type: MARKET or LIMIT.
        quantity: Order quantity.
        price: Order price (required for LIMIT, rejected for MARKET).

    Returns:
        dict: Validated order parameters.

    Raises:
        ValueError: If any input is invalid.
    """
    validated_type = validate_order_type(order_type)

    validated = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validated_type,
        "quantity": validate_quantity(quantity),
    }

    validated_price = validate_price(price, validated_type)
    if validated_price is not None:
        validated["price"] = validated_price

    logger.info("Input validation passed: %s", validated)
    return validated
