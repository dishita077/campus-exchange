# Campus Basic Necessities Exchange System

A simple DBMS + minimal Flask backend + static frontend for exchanging basic items on campus (notes, stationery, lab coats, calculators, umbrellas, books, etc).

## Quick start (local)
1. Create and activate a Python virtualenv:
```bash
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install flask flask-cors
```
2. Edit `app.py` and set your MySQL password (variable `DB_PASSWORD`) and optionally the DB user/host.
3. Run the backend:
```bash
python app.py
```
4. Open `http://127.0.0.1:5000` in the browser (it will call the backend).

## Project structure
```
campus-exchange/
├── README.md
├── campus_exchange.db
├── app.py
├── main.py

