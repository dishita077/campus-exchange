# Campus Basic Necessities Exchange System

A simple DBMS + minimal Flask backend + static frontend for exchanging basic items on campus (notes, stationery, lab coats, calculators, umbrellas, books, etc).

## What’s included
- `database.sql` — schema + sample data
- `backend/app.py` — small Flask REST API (replace DB password before running)
- `frontend/index.html` — minimal Bootstrap page that lists items

## Quick start (local)
1. Import the database:
```bash
mysql -u root -p < database.sql
```
2. Create and activate a Python virtualenv:
```bash
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
3. Edit `backend/app.py` and set your MySQL password (variable `DB_PASSWORD`) and optionally the DB user/host.
4. Run the backend:
```bash
python backend/app.py
```
5. Open `frontend/index.html` in the browser (it will call the backend at http://127.0.0.1:5000).

## Project structure
```
campus-exchange/
├── README.md
├── database.sql
├── backend/
│   └── app.py
├── frontend/
    └── index.html
