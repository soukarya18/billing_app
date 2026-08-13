from flask import Flask, render_template, request, jsonify
from datetime import date
from pathlib import Path
import json

app = Flask(__name__)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
BILLS_FILE = DATA_DIR / "bills.json"


def load_bills() -> list:
    """Load saved bills from the JSON file."""
    if not BILLS_FILE.exists():
        return []

    try:
        return json.loads(BILLS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_bills(bills: list) -> None:
    """Save bills to the JSON file."""
    BILLS_FILE.write_text(
        json.dumps(bills, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


@app.route("/")
def index():
    return render_template(
        "index.html",
        today=date.today().isoformat()
    )


@app.post("/api/save")
def save_bill():
    data = request.get_json(force=True)

    bill_no = str(data.get("bill_no", "")).strip()
    if not bill_no:
        return jsonify({
            "ok": False,
            "message": "Bill number is required."
        }), 400

    if not data.get("customer_name", "").strip():
        return jsonify({
            "ok": False,
            "message": "Customer name is required."
        }), 400

    items = data.get("items", [])
    if not items:
        return jsonify({
            "ok": False,
            "message": "Add at least one item."
        }), 400

    # Description is optional. A row is saved when it has either
    # a description, quantity, or rate.
    clean_items = []
    grand_total = 0.0

    for item in items:
        description = str(item.get("description", "")).strip()

        try:
            quantity = float(item.get("quantity", 0))
        except (TypeError, ValueError):
            quantity = 0

        try:
            rate = float(item.get("rate", 0))
        except (TypeError, ValueError):
            rate = 0

        if not description and quantity == 0 and rate == 0:
            continue

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
        return jsonify({
            "ok": False,
            "message": "Add a valid item."
        }), 400

    bills = load_bills()

    bill = {
        "bill_no": bill_no,
        "date": data.get("date", date.today().isoformat()),
        "shop_name": "S.I. GARMENTS",
        "shop_address": "S/73/1B, Marry Road, Kolkata-700018",
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
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
