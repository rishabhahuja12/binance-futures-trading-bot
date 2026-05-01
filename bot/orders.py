"""
Order placement logic.

Constructs order parameters, calls the client, and parses real API responses.
All output values come ONLY from the actual Binance API response.
No fabricated or placeholder values — ever.
"""

import logging

from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger("trading_bot")


def build_order_params(validated_input):
    """Construct API-ready order parameters from validated input.

    Args:
        validated_input: Dict returned by validate_order_input().

    Returns:
        dict: Parameters for futures_create_order().
    """
    params = {
        "symbol": validated_input["symbol"],
        "side": validated_input["side"],
        "type": validated_input["order_type"],
        "quantity": validated_input["quantity"],
    }

    if validated_input["order_type"] == "LIMIT":
        params["price"] = validated_input["price"]
        params["timeInForce"] = "GTC"

    return params


def parse_order_response(response):
    """Extract key fields from a real API response.

    Only returns fields that actually exist in the response.
    Never fabricates or assumes values.

    Args:
        response: Raw API response dict from Binance.

    Returns:
        dict: Parsed response with available fields.

    Raises:
        ValueError: If response format is unexpected.
    """
    if not isinstance(response, dict):
        logger.error("Unexpected response type: %s", type(response))
        raise ValueError("Unexpected response format from API")

    parsed = {}
    fields = [
        "orderId", "status", "executedQty", "avgPrice",
        "symbol", "side", "type", "origQty", "price", "timeInForce",
    ]

    for field in fields:
        if field in response:
            parsed[field] = response[field]

    if "orderId" not in parsed:
        logger.warning("Response missing 'orderId': %s", response)

    return parsed


def place_order(client, validated_input):
    """Place an order via the Binance client.

    Args:
        client: BinanceTestnetClient instance.
        validated_input: Dict from validate_order_input().

    Returns:
        dict: Parsed order response from the real API.

    Raises:
        BinanceAPIException: On API errors.
        BinanceRequestException: On request failures.
        ConnectionError: On network failures.
    """
    params = build_order_params(validated_input)

    logger.info(
        "Placing %s %s order: %s %s",
        params["type"], params["side"],
        params["quantity"], params["symbol"],
    )

    try:
        response = client.futures_create_order(**params)
    except BinanceAPIException as e:
        logger.error("Binance API error: %s (code: %s)", e.message, e.code)
        raise
    except BinanceRequestException as e:
        logger.error("Binance request error: %s", e)
        raise
    except ConnectionError as e:
        logger.error("Network error: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error placing order: %s", e)
        raise

    parsed = parse_order_response(response)
    logger.info("Order placed successfully: %s", parsed)
    return parsed
