from flask import Flask, render_template, request, jsonify
from datetime import date
from pathlib import Path
import json
import re

app = Flask(__name__)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
BILLS_FILE = DATA_DIR / "bills.json"


def load_bills() -> list:
    """Load all saved bills from the JSON file."""
    if not BILLS_FILE.exists():
        return []

    try:
        return json.loads(BILLS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_bills(bills: list) -> None:
    """Save all bills to the JSON file."""
    BILLS_FILE.write_text(
        json.dumps(bills, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def get_next_bill_no(bills: list | None = None) -> str:
    """Return the next available BILL-XXXX number."""
    if bills is None:
        bills = load_bills()

    highest_number = 0

    for bill in bills:
        bill_no = str(bill.get("bill_no", ""))
        match = re.fullmatch(r"BILL-(\d+)", bill_no, re.IGNORECASE)
        if match:
            highest_number = max(highest_number, int(match.group(1)))

    return f"BILL-{highest_number + 1:04d}"


@app.route("/")
def index():
    bills = load_bills()
    return render_template(
        "index.html",
        today=date.today().isoformat(),
        next_bill_no=get_next_bill_no(bills)
    )


@app.get("/api/next-bill-no")
def next_bill_no():
    """Return a fresh bill number for a new bill."""
    return jsonify({"bill_no": get_next_bill_no()})


@app.post("/api/save")
def save_bill():
    data = request.get_json(force=True)

    if not data.get("customer_name", "").strip():
        return jsonify({"ok": False, "message": "Customer name is required."}), 400

    items = data.get("items", [])
    if not items:
        return jsonify({"ok": False, "message": "Add at least one item."}), 400

    # Recalculate totals on the server so the saved bill is always accurate.
    clean_items = []
    grand_total = 0.0

    for item in items:
        description = str(item.get("description", "")).strip()
        if not description:
            continue

        try:
            quantity = float(item.get("quantity", 0))
            rate = float(item.get("rate", 0))
        except (TypeError, ValueError):
            quantity, rate = 0, 0

        amount = quantity * rate
        grand_total += amount

        clean_items.append({
            "description": description,
            "serial": len(clean_items) + 1,
            "quantity": quantity,
            "rate": rate,
            "amount": round(amount, 2)
        })

    if not clean_items:
        return jsonify({"ok": False, "message": "Add a valid item."}), 400

    bills = load_bills()

    # Always generate the bill number on the server to avoid duplicates.
    bill_no = get_next_bill_no(bills)

    bill = {
        "bill_no": bill_no,
        "date": data.get("date", date.today().isoformat()),
        "shop_name": data.get("shop_name", "").strip(),
        "shop_address": data.get("shop_address", "").strip(),
        "customer_name": data.get("customer_name", "").strip(),
        "customer_phone": data.get("customer_phone", "").strip(),
        "items": clean_items,
        "grand_total": round(grand_total, 2)
    }

    bills.append(bill)
    save_bills(bills)

    return jsonify({
        "ok": True,
        "message": f"Bill {bill_no} saved successfully.",
        "bill": bill
    })


@app.get("/api/bills")
def get_bills():
    return jsonify(load_bills())


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)