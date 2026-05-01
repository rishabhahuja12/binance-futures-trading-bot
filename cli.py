"""
CLI entry point for the Binance Futures Testnet Trading Bot.

Enhanced UX features:
- Pre-execution confirmation prompt (y/n)
- Clean, structured output formatting
- User-friendly error messages (full details logged to file)
- Validation feedback before any API call

User interface only — no business logic or API communication.
"""

import argparse
import sys
import logging

from bot.logging_config import setup_logging
from bot.client import BinanceTestnetClient
from bot.validators import validate_order_input
from bot.orders import place_order
from binance.exceptions import BinanceAPIException, BinanceRequestException


# ── Output Formatting ────────────────────────────────────────────

SEPARATOR_THICK = "=" * 50
SEPARATOR_THIN = "-" * 50


def print_order_summary(validated):
    """Print order summary BEFORE execution."""
    print()
    print(SEPARATOR_THICK)
    print(f"  Order Summary ({validated['order_type']})")
    print(SEPARATOR_THICK)
    print(f"  Symbol:     {validated['symbol']}")
    print(f"  Side:       {validated['side']}")
    print(f"  Type:       {validated['order_type']}")
    print(f"  Quantity:   {validated['quantity']}")
    if "price" in validated:
        print(f"  Price:      {validated['price']}")
    print(SEPARATOR_THICK)


def print_order_result(parsed):
    """Print structured order response AFTER execution.

    All values come from the real API response — never fabricated.
    """
    print()
    print(SEPARATOR_THIN)
    print("  Order Executed Successfully")
    print(SEPARATOR_THIN)
    print(f"  Order ID:       {parsed.get('orderId', 'N/A')}")
    print(f"  Status:         {parsed.get('status', 'N/A')}")
    print(f"  Symbol:         {parsed.get('symbol', 'N/A')}")
    print(f"  Side:           {parsed.get('side', 'N/A')}")
    print(f"  Type:           {parsed.get('type', 'N/A')}")
    print(f"  Orig Qty:       {parsed.get('origQty', 'N/A')}")
    print(f"  Executed Qty:   {parsed.get('executedQty', 'N/A')}")
    print(f"  Avg Price:      {parsed.get('avgPrice', 'N/A')}")
    if parsed.get('timeInForce'):
        print(f"  Time In Force:  {parsed['timeInForce']}")
    if parsed.get('price') and parsed.get('price') != '0.00':
        print(f"  Limit Price:    {parsed['price']}")
    print(SEPARATOR_THIN)
    print("  \u2713 Order placed successfully")
    print()


def print_error(message):
    """Print a user-friendly error message to the console."""
    print()
    print(SEPARATOR_THIN)
    print(f"  \u2717 {message}")
    print(SEPARATOR_THIN)
    print()


# ── Confirmation Prompt ──────────────────────────────────────────

def confirm_order():
    """Ask the user to confirm before placing the order.

    Returns:
        bool: True if user confirms, False otherwise.
    """
    try:
        answer = input("  Confirm order? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False

    return answer in ("y", "yes")


# ── Argument Parser ──────────────────────────────────────────────

def create_parser():
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY "
            "--type MARKET --quantity 0.01\n"
            "  python cli.py --symbol ETHUSDT --side SELL "
            "--type LIMIT --quantity 0.1 --price 3000\n"
        ),
    )

    parser.add_argument(
        "--symbol", required=True,
        help="Trading pair (e.g., BTCUSDT)",
    )
    parser.add_argument(
        "--side", required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type", required=True, dest="order_type",
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type: MARKET or LIMIT",
    )
    parser.add_argument(
        "--quantity", required=True, type=float,
        help="Order quantity (must be positive)",
    )
    parser.add_argument(
        "--price", type=float, default=None,
        help="Order price (required for LIMIT orders)",
    )

    return parser


# ── Main Entry Point ─────────────────────────────────────────────

def main():
    """Main CLI entry point."""
    logger = setup_logging()

    parser = create_parser()
    args = parser.parse_args()

    # --- Step 1: Validate inputs ---
    try:
        validated = validate_order_input(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValueError as e:
        logger.error("Validation error: %s", e)
        print_error(f"Invalid input: {e}")
        sys.exit(1)

    # --- Step 2: Print summary BEFORE execution ---
    print_order_summary(validated)

    # --- Step 3: Confirmation prompt ---
    if not confirm_order():
        logger.info("Order cancelled by user")
        print("\n  Order cancelled by user.\n")
        sys.exit(0)

    # --- Step 4: Initialize client ---
    try:
        client = BinanceTestnetClient()
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        print_error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error("Client init failed: %s", e)
        print_error(f"Failed to connect: {e}")
        sys.exit(1)

    # --- Step 5: Place order ---
    try:
        result = place_order(client, validated)
    except BinanceAPIException as e:
        logger.error("API error: %s (code: %s)", e.message, e.code)
        print_error(f"Order failed: {e.message} (code: {e.code})")
        sys.exit(1)
    except BinanceRequestException as e:
        logger.error("Request error: %s", e)
        print_error(f"Request failed: {e.message}")
        sys.exit(1)
    except ConnectionError as e:
        logger.error("Network error: %s", e)
        print_error("Network error: Could not connect to Binance. Check your internet.")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

    # --- Step 6: Print result AFTER execution ---
    print_order_result(result)


if __name__ == "__main__":
    main()
