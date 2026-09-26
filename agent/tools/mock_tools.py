import json
from pathlib import Path


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
MOCK_DATA_DIR = BASE_DIR / "mock_data"

CUSTOMERS_FILE = MOCK_DATA_DIR / "customers.json"
ORDERS_FILE = MOCK_DATA_DIR / "orders.json"
ACCOUNTS_FILE = MOCK_DATA_DIR / "accounts.json"


# ---------------------------------------------------------
# DATA LOADER
# ---------------------------------------------------------

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------
# CUSTOMER TOOL
# ---------------------------------------------------------

def get_customer(customer_id):
    """Return customer information for a given customer ID."""

    customers = load_json(CUSTOMERS_FILE)

    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer

    return None
# ACCOUNT TOOL
# -----------------------------------------------

def get_account(customer_id):
    """Return account information for a given customer ID."""

    accounts = load_json(ACCOUNTS_FILE)

    for account in accounts:
        if account["customer_id"] == customer_id:
            return account

    return None

# ---------------------------------------------------------
# BALANCE TOOL
# ---------------------------------------------------------

def get_balance(customer_id):
    """Return the current balance of a customer."""

    customer = get_customer(customer_id)

    if customer is None:
        return None

    return customer["balance"]


# ---------------------------------------------------------
# ORDER TOOL
# ---------------------------------------------------------

def get_order(order_id):
    """Return order information for a given order ID."""

    orders = load_json(ORDERS_FILE)

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return None


# ---------------------------------------------------------
# REFUND TOOL
# ---------------------------------------------------------

def issue_refund(customer_id, order_id, amount):
    """
    Simulate issuing a refund.

    This is only a mock tool.
    The actual governance decision will later be handled by SAARTHI.
    """

    customer = get_customer(customer_id)
    order = get_order(order_id)

    if customer is None:
        return {
            "success": False,
            "error": "CUSTOMER_NOT_FOUND"
        }

    if order is None:
        return {
            "success": False,
            "error": "ORDER_NOT_FOUND"
        }

    if order["customer_id"] != customer_id:
        return {
            "success": False,
            "error": "CUSTOMER_ORDER_MISMATCH"
        }

    if amount <= 0:
        return {
            "success": False,
            "error": "INVALID_REFUND_AMOUNT"
        }

    if amount > customer["eligible_refund"]:
        return {
            "success": False,
            "error": "REFUND_EXCEEDS_ELIGIBILITY"
        }

    return {
        "success": True,
        "customer_id": customer_id,
        "order_id": order_id,
        "refund_amount": amount,
        "status": "REFUND_READY"
    }


# ---------------------------------------------------------
# UPDATE CUSTOMER TOOL
# ---------------------------------------------------------

def update_customer(customer_id, updates):
    """Simulate updating customer information."""

    customers = load_json(CUSTOMERS_FILE)

    for customer in customers:

        if customer["customer_id"] == customer_id:

            customer.update(updates)

            return {
                "success": True,
                "customer": customer
            }

    return {
        "success": False,
        "error": "CUSTOMER_NOT_FOUND"
    }