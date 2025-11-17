"""
Single-file Flask app (SQLite) for Campus Exchange.

Features:
- Uses sqlite3 (file: campus_exchange.db)
- Creates schema and inserts 5-10 sample rows per table on first run
- REST endpoints for students, items, requests, approvals, exchanges
- Simple single-page frontend served at '/' (HTML + Vanilla JS + Bootstrap CDN)

Run:
    python campus_exchange_app.py

The web UI runs on http://127.0.0.1:5000/

Note: This file is intentionally self-contained so you can place it into a repo and run.
"""

from flask import Flask, request, jsonify, g, render_template_string
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

DB_PATH = 'campus_exchange.db'

app = Flask(__name__)
CORS(app)
app.config['JSON_SORT_KEYS'] = False

# ------------------ Database helpers ------------------
SCHEMA_SQL = r"""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Student (
  StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
  Name TEXT NOT NULL,
  Email TEXT UNIQUE,
  Phone TEXT,
  Department TEXT,
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Item (
  ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
  OwnerID INTEGER NOT NULL,
  ItemName TEXT NOT NULL,
  Category TEXT,
  Description TEXT,
  `Condition` TEXT,
  Status TEXT DEFAULT 'Available',
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (OwnerID) REFERENCES Student(StudentID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Request (
  RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
  ItemID INTEGER NOT NULL,
  RequesterID INTEGER NOT NULL,
  RequestDate DATE DEFAULT (date('now')),
  Status TEXT DEFAULT 'Pending',
  Message TEXT,
  FOREIGN KEY (ItemID) REFERENCES Item(ItemID) ON DELETE CASCADE,
  FOREIGN KEY (RequesterID) REFERENCES Student(StudentID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Exchange (
  ExchangeID INTEGER PRIMARY KEY AUTOINCREMENT,
  RequestID INTEGER UNIQUE NOT NULL,
  ExchangeDate DATE DEFAULT (date('now')),
  ReturnDate DATE NULL,
  Notes TEXT,
  FOREIGN KEY (RequestID) REFERENCES Request(RequestID) ON DELETE CASCADE
);
"""

SAMPLE_DATA_SQL = r"""
-- students (6 sample)
INSERT OR IGNORE INTO Student (StudentID, Name, Email, Phone, Department, CreatedAt) VALUES
(1,'Aditi Sharma','aditi@uni.edu','9876543210','CSE',datetime('now','-40 days')),
(2,'Rahul Singh','rahul@uni.edu','9876501234','ECE',datetime('now','-37 days')),
(3,'Neha Verma','neha@uni.edu','9812345678','ME',datetime('now','-30 days')),
(4,'Ankit Patel','ankit@uni.edu','9898989898','CSE',datetime('now','-25 days')),
(5,'Sana Khan','sana@uni.edu','9887766554','BIO',datetime('now','-18 days')),
(6,'Vikram Joshi','vikram@uni.edu','9900112233','EE',datetime('now','-10 days'));

-- items (8 sample)
INSERT OR IGNORE INTO Item (ItemID, OwnerID, ItemName, Category, Description, `Condition`, Status, CreatedAt) VALUES
(1,1,'Scientific Calculator','Electronics','Casio fx-991ES PLUS','Good','Available',datetime('now','-35 days')),
(2,2,'Lab Coat','Clothing','White lab coat size M','Like New','Available',datetime('now','-33 days')),
(3,3,'Linear Algebra Textbook','Books','Schaum\'s Outline: Linear Algebra, used','Fair','Available',datetime('now','-28 days')),
(4,4,'Bicycle Lock','Accessories','Combination U-lock, sturdy','Good','Available',datetime('now','-22 days')),
(5,1,'USB-C Charger','Electronics','20W fast charger','Good','Available',datetime('now','-20 days')),
(6,5,'Microscope Slides (box)','Lab Supplies','Set of 50 slides','New','Available',datetime('now','-15 days')),
(7,6,'Guitar','Instruments','Acoustic guitar with minor scratches','Fair','Available',datetime('now','-9 days')),
(8,2,'Protective Gloves','Lab Supplies','Latex gloves, medium, unopened box','New','Available',datetime('now','-8 days'));

-- requests (6 sample)
INSERT OR IGNORE INTO Request (RequestID, ItemID, RequesterID, RequestDate, Status, Message) VALUES
(1,1,2,date('now','-20 days'),'Approved','Could I borrow during exams?'),
(2,3,1,date('now','-18 days'),'Pending','Need for next week lab'),
(3,5,4,date('now','-14 days'),'Pending','Charger for my phone'),
(4,7,3,date('now','-7 days'),'Pending','Want to practice for performance'),
(5,2,6,date('now','-6 days'),'Rejected','Require for a lab demo'),
(6,6,5,date('now','-4 days'),'Pending','For biology practical');

-- exchanges (3 sample)
INSERT OR IGNORE INTO Exchange (ExchangeID, RequestID, ExchangeDate, ReturnDate, Notes) VALUES
(1,1,date('now','-19 days'),date('now','-5 days'),'Returned in good condition'),
(2,5,date('now','-5 days'),NULL,'Rejected request recorded'),
(3,2,date('now','-2 days'),NULL,'Initial exchange started');
"""


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        need_init = not os.path.exists(DB_PATH)
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        if need_init:
            init_db(db)
    return db


def init_db(db_conn):
    cur = db_conn.cursor()
    # execute schema
    for stmt in SCHEMA_SQL.split(';'):
        s = stmt.strip()
        if s:
            cur.execute(s)
    # load sample data
    # sqlite's executescript can run multiple statements
    cur.executescript(SAMPLE_DATA_SQL)
    db_conn.commit()
    print('Initialized DB and inserted sample data')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# ------------------ API endpoints ------------------
@app.route('/students', methods=['GET','POST'])
def students():
    db = get_db(); cur = db.cursor()
    if request.method == 'POST':
        data = request.json
        cur.execute("INSERT INTO Student (Name, Email, Phone, Department) VALUES (?,?,?,?)",
                    (data.get('Name'), data.get('Email'), data.get('Phone'), data.get('Department')))
        db.commit()
        return jsonify({'message':'Student created'}), 201
    else:
        cur.execute("SELECT * FROM Student ORDER BY CreatedAt DESC")
        rows = [dict(r) for r in cur.fetchall()]
        return jsonify(rows)


@app.route('/items', methods=['GET','POST'])
def items():
    db = get_db(); cur = db.cursor()
    if request.method == 'POST':
        data = request.json
        cur.execute("INSERT INTO Item (OwnerID, ItemName, Category, Description, `Condition`) VALUES (?,?,?,?,?)",
                    (data['OwnerID'], data['ItemName'], data.get('Category'), data.get('Description'), data.get('Condition')))
        db.commit()
        return jsonify({'message':'Item posted'}), 201
    else:
        # optional ?category= or ?owner=
        category = request.args.get('category')
        owner = request.args.get('owner')
        q = "SELECT i.*, s.Name as OwnerName FROM Item i JOIN Student s ON i.OwnerID = s.StudentID"
        params = []
        if category:
            q += " WHERE i.Category = ?"
            params.append(category)
        elif owner:
            q += " WHERE i.OwnerID = ?"
            params.append(owner)
        q += " ORDER BY i.CreatedAt DESC"
        cur.execute(q, params)
        rows = [dict(r) for r in cur.fetchall()]
        return jsonify(rows)


@app.route('/request', methods=['POST'])
def create_request():
    data = request.json
    db = get_db(); cur = db.cursor()
    cur.execute("INSERT INTO Request (ItemID, RequesterID, Message) VALUES (?,?,?)",
                (data['ItemID'], data['RequesterID'], data.get('Message')))
    # set item status to Requested
    cur.execute("UPDATE Item SET Status = 'Requested' WHERE ItemID = ?", (data['ItemID'],))
    db.commit()
    return jsonify({'message':'Request created'}), 201


@app.route('/requests/<int:item_id>', methods=['GET'])
def get_requests(item_id):
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT r.*, s.Name as RequesterName FROM Request r JOIN Student s ON r.RequesterID = s.StudentID WHERE r.ItemID=? ORDER BY r.RequestDate DESC", (item_id,))
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)


@app.route('/approve_request', methods=['POST'])
def approve_request():
    data = request.json  # expects {request_id: int}
    rid = data['request_id']
    db = get_db(); cur = db.cursor()
    # update request
    cur.execute("UPDATE Request SET Status = 'Approved' WHERE RequestID = ?", (rid,))
    # get item id
    cur.execute("SELECT ItemID FROM Request WHERE RequestID = ?", (rid,))
    item = cur.fetchone()
    if not item:
        return jsonify({'error':'Request not found'}), 404
    item_id = item['ItemID']
    # update item status
    cur.execute("UPDATE Item SET Status = 'Not Available' WHERE ItemID = ?", (item_id,))
    # insert exchange record
    cur.execute("INSERT INTO Exchange (RequestID) VALUES (?)", (rid,))
    db.commit()
    return jsonify({'message':'Request approved and exchange recorded'}), 200


@app.route('/exchanges', methods=['GET'])
def exchanges():
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT e.*, r.ItemID, s.Name as RequesterName FROM Exchange e JOIN Request r ON e.RequestID = r.RequestID JOIN Student s ON r.RequesterID = s.StudentID ORDER BY e.ExchangeDate DESC")
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)


# ------------------ Simple Frontend ------------------
INDEX_HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Campus Exchange</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-4">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h1 class="h3">Campus Exchange</h1>
    <div>
      <button class="btn btn-sm btn-outline-primary" onclick="loadAll()">Refresh</button>
    </div>
  </div>

  <div class="row">
    <div class="col-md-6">
      <div class="card mb-3">
        <div class="card-body">
          <h5>Post new item</h5>
          <form id="postItemForm" onsubmit="postItem(event)">
            <div class="mb-2">
              <label class="form-label">OwnerID</label>
              <input required class="form-control" id="ownerID" />
            </div>
            <div class="mb-2">
              <label class="form-label">Item name</label>
              <input required class="form-control" id="itemName" />
            </div>
            <div class="mb-2">
              <label class="form-label">Category</label>
              <input class="form-control" id="category" />
            </div>
            <div class="mb-2">
              <label class="form-label">Condition</label>
              <input class="form-control" id="condition" />
            </div>
            <div class="mb-2">
              <label class="form-label">Description</label>
              <textarea class="form-control" id="description"></textarea>
            </div>
            <button class="btn btn-primary btn-sm" type="submit">Post</button>
          </form>
        </div>
      </div>

      <div class="card">
        <div class="card-body">
          <h5>Items</h5>
          <div id="itemsList">Loading...</div>
        </div>
      </div>
    </div>

    <div class="col-md-6">
      <div class="card mb-3">
        <div class="card-body">
          <h5>Make a request</h5>
          <form id="makeRequestForm" onsubmit="makeRequest(event)">
            <div class="mb-2">
              <label class="form-label">ItemID</label>
              <input required class="form-control" id="reqItemID" />
            </div>
            <div class="mb-2">
              <label class="form-label">RequesterID</label>
              <input required class="form-control" id="reqRequesterID" />
            </div>
            <div class="mb-2">
              <label class="form-label">Message</label>
              <textarea class="form-control" id="reqMessage"></textarea>
            </div>
            <button class="btn btn-success btn-sm" type="submit">Request</button>
          </form>
        </div>
      </div>

      <div class="card mb-3">
        <div class="card-body">
          <h5>Requests for an Item</h5>
          <div class="input-group mb-2">
            <input id="requestsItemId" class="form-control" placeholder="Item ID" />
            <button class="btn btn-outline-secondary" onclick="loadRequests()">Load</button>
          </div>
          <div id="requestsList">—</div>
        </div>
      </div>

      <div class="card">
        <div class="card-body">
          <h5>Admin (approve requests)</h5>
          <p class="small text-muted">Enter request id and click Approve</p>
          <div class="input-group mb-2">
            <input id="approveReqId" class="form-control" placeholder="Request ID" />
            <button class="btn btn-primary" onclick="approveReq()">Approve</button>
          </div>
          <div id="adminMsg"></div>
        </div>
      </div>

    </div>
  </div>
</div>

<script>
async function loadAll(){
  const res = await fetch('/items');
  const items = await res.json();
  const container = document.getElementById('itemsList');
  if(!items.length) { container.innerHTML = '<div class="text-muted">No items</div>'; return; }
  container.innerHTML = '';
  items.forEach(i => {
    const card = document.createElement('div');
    card.className = 'mb-2 border rounded p-2 bg-white';
    card.innerHTML = `<strong>${i.ItemName}</strong> <small class="text-muted">(#${i.ItemID})</small><br>
      <small>Owner: ${i.OwnerName} (ID ${i.OwnerID}) — ${i.Category || ''} — ${i.Condition || ''}</small>
      <div class="mt-1">${i.Description || ''}</div>
      <div class="mt-2"><button class="btn btn-sm btn-outline-primary" onclick="prefillRequest(${i.ItemID})">Request</button></div>`;
    container.appendChild(card);
  });
}

function prefillRequest(itemId){
  document.getElementById('reqItemID').value = itemId;
}

async function postItem(e){
  e.preventDefault();
  const payload = {
    OwnerID: parseInt(document.getElementById('ownerID').value),
    ItemName: document.getElementById('itemName').value,
    Category: document.getElementById('category').value,
    Description: document.getElementById('description').value,
    Condition: document.getElementById('condition').value
  };
  const r = await fetch('/items',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(r.ok){ alert('Posted'); loadAll(); document.getElementById('postItemForm').reset(); }
  else alert('Error');
}

async function makeRequest(e){
  e.preventDefault();
  const payload = {
    ItemID: parseInt(document.getElementById('reqItemID').value),
    RequesterID: parseInt(document.getElementById('reqRequesterID').value),
    Message: document.getElementById('reqMessage').value
  };
  const r = await fetch('/request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(r.ok){ alert('Request created'); document.getElementById('makeRequestForm').reset(); }
  else alert('Error creating request');
}

async function loadRequests(){
  const id = document.getElementById('requestsItemId').value;
  if(!id) return alert('Enter item id');
  const res = await fetch('/requests/'+id);
  const list = await res.json();
  const container = document.getElementById('requestsList');
  if(!list.length){ container.innerHTML = '<div class="text-muted">No requests</div>'; return; }
  container.innerHTML = '';
  list.forEach(r => {
    const el = document.createElement('div');
    el.className = 'mb-2 p-2 border rounded bg-white';
    el.innerHTML = `<div><strong>Request #${r.RequestID}</strong> by ${r.RequesterName} (ID ${r.RequesterID})</div>
      <div>${r.Message || ''}</div>
      <div class="text-muted small">Status: ${r.Status} — ${r.RequestDate}</div>`;
    container.appendChild(el);
  });
}

async function approveReq(){
  const id = document.getElementById('approveReqId').value;
  if(!id) return alert('Enter request id');
  const r = await fetch('/approve_request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request_id: parseInt(id)})});
  const res = await r.json();
  document.getElementById('adminMsg').innerText = res.message || res.error;
  loadAll();
}

// initial load
loadAll();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


if __name__ == '__main__':
    # initialize DB inside an application context to avoid "working outside of application context" errors
    with app.app_context():
        db = get_db()   # safe: g and app context available; will init DB if needed
        # close immediately; teardown will also close when the app context ends
        db.close()
    print('Starting Campus Exchange app — DB:', DB_PATH)
    app.run(debug=True)
