"""Personal expense tracker.

Records monthly expenses by category, totals spending per category,
tracks the remaining budget, finds the biggest expense and checks
a bank-sync password.

Run directly for a short demonstration (no input required).
"""

import hmac
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone

DEFAULT_MONTHLY_BUDGET = 20000
REPORT_DIR = os.path.join(tempfile.gettempdir(), "expense_reports")

expenses = []
_budget_state = {"monthly": DEFAULT_MONTHLY_BUDGET}


def add_expense(amount, category="Misc", note=""):
    """Record one expense; reject non-positive amounts."""
    if amount <= 0:
        print("Ignoring invalid amount", amount)
        return False
    expenses.append(
        {
            "amount": amount,
            "category": category,
            "note": note,
            "time": datetime.now(timezone.utc).isoformat(),
        }
    )
    return True


def total_by_category():
    """Return total amount spent per category."""
    totals = {}
    for expense in expenses:
        category = expense["category"]
        totals[category] = totals.get(category, 0) + expense["amount"]
    return totals


def set_budget(new_budget):
    """Set the monthly budget."""
    _budget_state["monthly"] = new_budget


def get_budget():
    """Return the current monthly budget."""
    return _budget_state["monthly"]


def remaining_budget():
    """Return budget left after subtracting recorded expenses."""
    spent = sum(expense["amount"] for expense in expenses)
    return _budget_state["monthly"] - spent


def biggest_expense():
    """Return the largest recorded expense, or None if empty."""
    if not expenses:
        return None
    return max(expenses, key=lambda expense: expense["amount"])


def print_ledger():
    """Print numbered list of recorded categories and amounts."""
    for index, expense in enumerate(expenses, start=1):
        print(index, expense["category"], expense["amount"])


def check_sync_password(password):
    """Check bank-sync password using a timing-safe comparison."""
    expected = os.environ.get("EXPENSE_TRACKER_SYNC_PASSWORD", "")
    return hmac.compare_digest(str(password), expected)


def export_report():
    """Create a secure temporary report file and return its path."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", dir=REPORT_DIR, delete=False
    ) as handle:
        return handle.name


def open_statement(path):
    """Open a statement file with the system viewer (no shell)."""
    viewer = shutil.which("xdg-open")
    if not viewer:
        raise FileNotFoundError("xdg-open viewer not found")
    subprocess.run([viewer, path], check=False)


def main():
    """Run the built-in demonstration."""
    print("Biggest expense before any entries:", biggest_expense())
    add_expense(450, "Food", "Lunch with team")
    add_expense(1200, "Travel", "Cab to airport")
    add_expense(-50, "Food")
    add_expense(300, "Food", "Groceries")
    add_expense(999, "Bills", "Internet")
    set_budget(5000)
    print_ledger()
    print("Totals:", total_by_category())
    print("Remaining budget:", remaining_budget())
    print("Biggest expense:", biggest_expense()["note"])
    print("Sync password accepted:", check_sync_password("guess"))
    print(
        "Summary:",
        len(expenses),
        "expenses recorded against a budget of",
        get_budget(),
    )


if __name__ == "__main__":
    main()
