"""Tests for CLI argument parsing and validation behaviour."""

import pytest
from unittest.mock import patch
from cli import create_parser, confirm_order


class TestCLIParser:
    """Test argparse argument parsing."""

    def test_valid_market_args(self):
        parser = create_parser()
        args = parser.parse_args([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--type", "MARKET",
            "--quantity", "0.01",
        ])
        assert args.symbol == "BTCUSDT"
        assert args.side == "BUY"
        assert args.order_type == "MARKET"
        assert args.quantity == 0.01
        assert args.price is None

    def test_valid_limit_args(self):
        parser = create_parser()
        args = parser.parse_args([
            "--symbol", "ETHUSDT",
            "--side", "SELL",
            "--type", "LIMIT",
            "--quantity", "0.1",
            "--price", "3000",
        ])
        assert args.symbol == "ETHUSDT"
        assert args.order_type == "LIMIT"
        assert args.price == 3000.0

    def test_missing_symbol_raises(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                "--side", "BUY",
                "--type", "MARKET",
                "--quantity", "0.01",
            ])

    def test_missing_side_raises(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                "--symbol", "BTCUSDT",
                "--type", "MARKET",
                "--quantity", "0.01",
            ])

    def test_missing_type_raises(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                "--symbol", "BTCUSDT",
                "--side", "BUY",
                "--quantity", "0.01",
            ])

    def test_missing_quantity_raises(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                "--symbol", "BTCUSDT",
                "--side", "BUY",
                "--type", "MARKET",
            ])

    def test_invalid_side_choice_raises(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                "--symbol", "BTCUSDT",
                "--side", "HOLD",
                "--type", "MARKET",
                "--quantity", "0.01",
            ])

    def test_invalid_type_choice_raises(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                "--symbol", "BTCUSDT",
                "--side", "BUY",
                "--type", "STOP",
                "--quantity", "0.01",
            ])

    def test_lowercase_side_accepted(self):
        parser = create_parser()
        args = parser.parse_args([
            "--symbol", "BTCUSDT",
            "--side", "buy",
            "--type", "MARKET",
            "--quantity", "0.01",
        ])
        assert args.side == "buy"

    def test_lowercase_type_accepted(self):
        parser = create_parser()
        args = parser.parse_args([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--type", "limit",
            "--quantity", "0.01",
            "--price", "60000",
        ])
        assert args.order_type == "limit"


class TestConfirmOrder:
    """Test pre-execution confirmation prompt."""

    @patch("builtins.input", return_value="y")
    def test_confirm_yes(self, mock_input):
        assert confirm_order() is True

    @patch("builtins.input", return_value="yes")
    def test_confirm_yes_full(self, mock_input):
        assert confirm_order() is True

    @patch("builtins.input", return_value="Y")
    def test_confirm_yes_uppercase(self, mock_input):
        assert confirm_order() is True

    @patch("builtins.input", return_value="n")
    def test_confirm_no(self, mock_input):
        assert confirm_order() is False

    @patch("builtins.input", return_value="")
    def test_confirm_empty(self, mock_input):
        assert confirm_order() is False

    @patch("builtins.input", return_value="anything")
    def test_confirm_random_input(self, mock_input):
        assert confirm_order() is False

    @patch("builtins.input", side_effect=EOFError)
    def test_confirm_eof(self, mock_input):
        assert confirm_order() is False

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_confirm_keyboard_interrupt(self, mock_input):
        assert confirm_order() is False
