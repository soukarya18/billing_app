# Simple Billing App

A small Flask billing application matching the requested layout:

Description | S.No | Quantity | Rate | Amount

Features:
- Shop name and address
- Bill number and date
- Customer name and phone number
- Add/delete items
- Automatic Amount = Quantity × Rate
- Automatic Grand Total
- Save bills to data/bills.json
- Print-friendly bill
- Mobile-friendly layout

## Run on Windows

1. Install Python 3.10+.
2. Open Command Prompt in this folder.
3. Install dependencies:

   pip install -r requirements.txt

4. Start:

   python app.py

5. Open:

   http://127.0.0.1:5000

## Run on Linux/macOS

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

Then open http://127.0.0.1:5000

The saved bills are stored locally in:
data/bills.json
