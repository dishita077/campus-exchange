#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

os.remove("campus_exchange.db")
DB_PATH = 'campus_exchange.db'

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
-- students (8 sample)
INSERT OR IGNORE INTO Student (StudentID, Name, Email, Phone, Department, CreatedAt) VALUES
(1,'Aditi Sharma','aditi@uni.edu','9876543210','CSE',datetime('now','-40 days')),
(2,'Rahul Singh','rahul@uni.edu','9876501234','ECE',datetime('now','-37 days')),
(3,'Neha Verma','neha@uni.edu','9812345678','ME',datetime('now','-30 days')),
(4,'Ankit Patel','ankit@uni.edu','9898989898','CSE',datetime('now','-25 days')),
(5,'Sana Khan','sana@uni.edu','9887766554','BIO',datetime('now','-18 days')),
(6,'Vikram Joshi','vikram@uni.edu','9900112233','EE',datetime('now','-10 days')),
(7,'Karan Mehta','karan@uni.edu','9811198765','CSE',datetime('now','-8 days')),
(8,'Ritu Jain','ritu@uni.edu','9800567890','ECE',datetime('now','-5 days'));

-- items (12 sample)
INSERT OR IGNORE INTO Item (ItemID, OwnerID, ItemName, Category, Description, `Condition`, Status, CreatedAt) VALUES
(1,1,'Scientific Calculator','Electronics','Casio fx-991ES PLUS','Good','Available',datetime('now','-35 days')),
(2,2,'Lab Coat','Clothing','White lab coat size M','Like New','Available',datetime('now','-33 days')),
(3,3,'Linear Algebra Textbook','Books','Schaum''s Outline: Linear Algebra, used','Fair','Available',datetime('now','-28 days')),
(4,4,'Bicycle Lock','Accessories','Combination U-lock, sturdy','Good','Available',datetime('now','-22 days')),
(5,1,'USB-C Charger','Electronics','20W fast charger','Good','Available',datetime('now','-20 days')),
(6,5,'Microscope Slides (box)','Lab Supplies','Set of 50 slides','New','Available',datetime('now','-15 days')),
(7,6,'Guitar','Instruments','Acoustic guitar with minor scratches','Fair','Available',datetime('now','-9 days')),
(8,2,'Protective Gloves','Lab Supplies','Latex gloves, medium, unopened box','New','Available',datetime('now','-8 days')),
(9,7,'Physics Notebook','Books','Full semester handwritten notes','Good','Available',datetime('now','-6 days')),
(10,3,'Drawing Kit','Accessories','Engineering drawing kit complete','Like New','Available',datetime('now','-5 days')),
(11,8,'Mini Tripod','Electronics','Portable phone tripod','Good','Available',datetime('now','-4 days')),
(12,4,'Sports Bottle','Accessories','1L BPA-free bottle','New','Available',datetime('now','-3 days'));

-- requests (10 sample)
INSERT OR IGNORE INTO Request (RequestID, ItemID, RequesterID, RequestDate, Status, Message) VALUES
(1,1,2,date('now','-20 days'),'Approved','Could I borrow during exams?'),
(2,3,1,date('now','-18 days'),'Pending','Need for next week lab'),
(3,5,4,date('now','-14 days'),'Approved','Charger for my phone'),
(4,7,3,date('now','-7 days'),'Pending','Want to practice for performance'),
(5,2,6,date('now','-6 days'),'Rejected','Require for a lab demo'),
(6,6,5,date('now','-4 days'),'Pending','For biology practical'),
(7,9,8,date('now','-3 days'),'Pending','Need notes for revision'),
(8,10,7,date('now','-2 days'),'Pending','Drawing kit needed urgently'),
(9,1,3,date('now','-1 days'),'Approved','Can I borrow calculator?'),
(10,12,2,date('now','-1 days'),'Pending','Need bottle for gym');

-- exchanges (5 sample)
INSERT OR IGNORE INTO Exchange (ExchangeID, RequestID, ExchangeDate, ReturnDate, Notes) VALUES
(1,1,date('now','-19 days'),date('now','-5 days'),'Returned in good condition'),
(2,5,date('now','-5 days'),NULL,'Rejected request recorded'),
(3,2,date('now','-2 days'),NULL,'Initial exchange started'),
(4,7,date('now','-1 days'),NULL,'Borrowed recently'),
(5,3,date('now','-13 days'),date('now','-1 days'),'Charger loaned and returned');
"""

PREDEFINED_QUERIES = {
    '1': {
        'desc': 'List all students (most recent first)',
        'sql': "SELECT StudentID, Name, Email, Department, CreatedAt FROM Student ORDER BY CreatedAt DESC"
    },
    '2': {
        'desc': 'List all available items with owner name',
        'sql': "SELECT i.ItemID, i.ItemName, i.Category, i.Condition, i.Status, s.StudentID as OwnerID, s.Name as OwnerName, i.CreatedAt FROM Item i JOIN Student s ON i.OwnerID = s.StudentID WHERE i.Status = 'Available' ORDER BY i.CreatedAt DESC"
    },
    '3': {
        'desc': 'Requests for a given item id',
        'sql': "SELECT r.RequestID, r.ItemID, r.RequesterID, s.Name as RequesterName, r.RequestDate, r.Status, r.Message FROM Request r JOIN Student s ON r.RequesterID = s.StudentID WHERE r.ItemID = ? ORDER BY r.RequestDate DESC"
    },
    '4': {
        'desc': 'Approved requests and their exchange records',
        'sql': "SELECT r.RequestID, r.ItemID, r.RequesterID, r.Status as RequestStatus, e.ExchangeID, e.ExchangeDate, e.ReturnDate, e.Notes FROM Request r LEFT JOIN Exchange e ON r.RequestID = e.RequestID WHERE r.Status = 'Approved' ORDER BY e.ExchangeDate DESC"
    },
    '5': {
        'desc': 'Items grouped by category (count)',
        'sql': "SELECT Category, COUNT(*) as NumItems FROM Item GROUP BY Category ORDER BY NumItems DESC"
    },
    '6': {
        'desc': 'Total requests per item (including 0)',
        'sql': "SELECT i.ItemID, i.ItemName, COALESCE(COUNT(r.RequestID),0) as RequestCount FROM Item i LEFT JOIN Request r ON i.ItemID = r.ItemID GROUP BY i.ItemID ORDER BY RequestCount DESC"
    }
}


def init_db(conn):
    cur = conn.cursor()
    # execute schema statements
    for stmt in SCHEMA_SQL.split(';'):
        s = stmt.strip()
        if not s:
            continue
        cur.execute(s)
    # load sample data
    cur.executescript(SAMPLE_DATA_SQL)
    conn.commit()
    print('Initialized DB and inserted sample data')


def get_db(path=DB_PATH):
    need_init = not os.path.exists(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    if need_init:
        init_db(conn)
    return conn


def print_rows(rows):
    if not rows:
        print('(no rows)')
        return
    cols = rows[0].keys()
    str_rows = [[str(r[c]) if r[c] is not None else 'NULL' for c in cols] for r in rows]
    widths = [max(len(str(c)), max(len(row[i]) for row in str_rows)) for i, c in enumerate(cols)]

    line = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
    print(line)
    header = '|' + '|'.join(' ' + str(c).ljust(widths[i]) + ' ' for i, c in enumerate(cols)) + '|'
    print(header)
    print(line)
    for r in str_rows:
        row_line = '|' + '|'.join(' ' + r[i].ljust(widths[i]) + ' ' for i in range(len(cols))) + '|'
        print(row_line)
    print(line)


def run_query(conn, key):
    q = PREDEFINED_QUERIES[key]['sql']
    cur = conn.cursor()
    if '?' in q:
        # prompt for param
        param = input('Enter parameter for query (e.g., item id): ').strip()
        cur.execute(q, (param,))
    else:
        cur.execute(q)
    rows = cur.fetchall()
    # convert sqlite Row to dict-like for printing
    rows = [dict(r) for r in rows]
    print('\n--', PREDEFINED_QUERIES[key]['desc'], '--')
    print_rows(rows)


def interactive_cli():
    conn = get_db()
    try:
        while True:
            print('\nPredefined queries:')
            for k, v in PREDEFINED_QUERIES.items():
                print(f" {k}. {v['desc']}")
            print(' q. quit')
            choice = input('\nChoose query number (or q): ').strip()
            if choice.lower() in ('q', 'quit', 'exit'):
                break
            if choice not in PREDEFINED_QUERIES:
                print('Invalid choice')
                continue
            run_query(conn, choice)
    finally:
        conn.close()


if __name__ == '__main__':
    # ensure DB exists and is initialized
    get_db()
    print('\nDatabase ready at:', DB_PATH)
    print('Run the script again to start the interactive query CLI.')
    # start interactive CLI
    interactive_cli()
