# Binance Futures Testnet Trading Bot

> ⚠️ This project uses Binance Futures **Testnet only**. No real funds are used.

A CLI-based trading bot that places **MARKET** and **LIMIT** orders on Binance Futures Testnet (USDT-M) with structured logging, input validation, proper error handling, and enhanced CLI UX.

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd trading_bot
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```
API_KEY=your_binance_testnet_api_key
API_SECRET=your_binance_testnet_api_secret
BASE_URL=https://testnet.binancefuture.com
```

> Get credentials from: https://testnet.binancefuture.com

---

## Usage

### Place a MARKET order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

You will be prompted:

```
Confirm order? (y/n):
```

---

### Place a LIMIT order

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3000
```

You will be prompted:

```
Confirm order? (y/n):
```

---

### CLI Arguments

| Argument     | Required   | Description                        |
|--------------|------------|------------------------------------|
| `--symbol`   | Yes        | Trading pair (e.g., BTCUSDT)       |
| `--side`     | Yes        | BUY or SELL                        |
| `--type`     | Yes        | MARKET or LIMIT                    |
| `--quantity` | Yes        | Order quantity (positive number)   |
| `--price`    | LIMIT only | Order price (required for LIMIT)   |

---

## CLI Enhancements

The CLI includes the following usability improvements:

- **Confirmation prompt** before placing any order
- **Formatted output** with clear sections for readability
- **User-friendly error messages** instead of raw exceptions
- **Immediate validation feedback** for invalid inputs

If the user declines confirmation, the order is safely cancelled:

```
Order cancelled by user.
```

- Confirmation accepts `y` / `yes` (case-insensitive)
- Any other input cancels the order

---

## How It Works

1. CLI parses user input
2. Inputs are validated
3. User confirms the order (y/n)
4. Order parameters are constructed
5. Request is sent to Binance Testnet
6. Response is parsed and displayed
7. All actions are logged

---

## Sample Output

### MARKET Order

```
==================================================
  Placing MARKET order:
  Symbol:   BTCUSDT
  Side:     BUY
  Quantity: 0.01
==================================================

Confirm order? (y/n): y

--------------------------------------------------
  Order Response:
  Order ID:     13096986994
  Status:       NEW
  Executed Qty: 0.0100
  Avg Price:    0.00
--------------------------------------------------
  ✓ Order placed successfully
```

### LIMIT Order

```
==================================================
  Placing LIMIT order:
  Symbol:   ETHUSDT
  Side:     SELL
  Quantity: 0.1
  Price:    3000.0
==================================================

Confirm order? (y/n): y

--------------------------------------------------
  Order Response:
  Order ID:     8676848095
  Status:       NEW
  Executed Qty: 0.000
  Avg Price:    0.00
--------------------------------------------------
  ✓ Order placed successfully
```

### Cancelled Order

```
==================================================
  Placing MARKET order:
  Symbol:   BTCUSDT
  Side:     BUY
  Quantity: 0.01
==================================================

Confirm order? (y/n): n

Order cancelled by user.
```

### Example Error

```
✗ API Error [-1121]: Invalid symbol.
```

---

## Error Handling

The application handles:
- Invalid user input (CLI validation)
- Binance API errors (e.g., invalid symbol, insufficient balance)
- Network failures

Errors are:
- Logged to file
- Displayed as user-friendly messages
- Do not crash the program

---

## Logging

Logs are written to:

```
logs/trading.log
```

Includes:
- API request details (without secrets)
- API responses
- Errors and warnings

Log levels:
- `INFO` → normal operations
- `WARNING` → unexpected but recoverable
- `ERROR` → failures

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py          # Binance client wrapper (API communication only)
    orders.py          # Order construction and placement logic
    validators.py      # Input validation
    logging_config.py  # Logging setup (file + console)
  tests/
    __init__.py
    test_validators.py # Unit tests for input validation
    test_orders.py     # Unit tests for order logic (mocked API)
    test_cli.py        # CLI argument parsing tests
  cli.py               # CLI entry point
  .env                 # API credentials (not committed)
  .gitignore
  requirements.txt
  README.md
```

---

## Assumptions

- Uses **Binance Futures Testnet** only (`https://testnet.binancefuture.com`)
- Uses `python-binance` library for API interactions
- `timeInForce` defaults to `GTC` for LIMIT orders
- All output values come directly from real API responses — no fabricated data
- Logs are written to `logs/trading.log`

---

## Security

- API keys loaded from `.env` via `python-dotenv`
- `.env` is in `.gitignore` — never committed
- Secrets are never logged or printed to console

