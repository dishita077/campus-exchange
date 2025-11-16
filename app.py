from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# === CONFIG ===
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "CHANGE_ME"   # <-- replace with your MySQL root password
DB_NAME = "campus_exchange"

def get_db():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                           db=DB_NAME, cursorclass=pymysql.cursors.DictCursor, autocommit=False)

@app.route('/students', methods=['GET','POST'])
def students():
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        data = request.json
        cur.execute("INSERT INTO Student (Name, Email, Phone, Department) VALUES (%s,%s,%s,%s)",
                    (data.get('Name'), data.get('Email'), data.get('Phone'), data.get('Department')))
        conn.commit()
        conn.close()
        return jsonify({'message':'Student created'}), 201
    else:
        cur.execute("SELECT * FROM Student")
        rows = cur.fetchall()
        conn.close()
        return jsonify(rows)

@app.route('/items', methods=['GET','POST'])
def items():
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        data = request.json
        cur.execute("INSERT INTO Item (OwnerID, ItemName, Category, Description, `Condition`) VALUES (%s,%s,%s,%s,%s)",
                    (data['OwnerID'], data['ItemName'], data.get('Category'), data.get('Description'), data.get('Condition')))
        conn.commit()
        conn.close()
        return jsonify({'message':'Item posted'}), 201
    else:
        cur.execute("SELECT i.*, s.Name as OwnerName FROM Item i JOIN Student s ON i.OwnerID = s.StudentID")
        rows = cur.fetchall()
        conn.close()
        return jsonify(rows)

@app.route('/request', methods=['POST'])
def create_request():
    data = request.json
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO Request (ItemID, RequesterID, Message) VALUES (%s,%s,%s)",
                (data['ItemID'], data['RequesterID'], data.get('Message')))
    conn.commit()
    # set item status to Requested
    cur.execute("UPDATE Item SET Status = 'Requested' WHERE ItemID = %s", (data['ItemID'],))
    conn.commit()
    conn.close()
    return jsonify({'message':'Request created'}), 201

@app.route('/requests/<int:item_id>', methods=['GET'])
def get_requests(item_id):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT r.*, s.Name as RequesterName FROM Request r JOIN Student s ON r.RequesterID = s.StudentID WHERE r.ItemID=%s", (item_id,))
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/approve_request', methods=['POST'])
def approve_request():
    data = request.json  # expects {request_id: int}
    rid = data['request_id']
    conn = get_db(); cur = conn.cursor()
    # update request
    cur.execute("UPDATE Request SET Status = 'Approved' WHERE RequestID = %s", (rid,))
    # get item id
    cur.execute("SELECT ItemID FROM Request WHERE RequestID = %s", (rid,))
    item = cur.fetchone()
    item_id = item['ItemID']
    # update item status
    cur.execute("UPDATE Item SET Status = 'Not Available' WHERE ItemID = %s", (item_id,))
    # insert exchange record
    cur.execute("INSERT INTO Exchange (RequestID) VALUES (%s)", (rid,))
    conn.commit()
    conn.close()
    return jsonify({'message':'Request approved and exchange recorded'}), 200

if __name__ == '__main__':
    app.run(debug=True)
