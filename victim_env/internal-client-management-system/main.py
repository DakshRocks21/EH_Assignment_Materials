from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Path to SQLite DB (in project root)
DATABASE = os.path.join(os.path.dirname(__file__), 'clients.db')

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clients(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT
            )
        ''')
        conn.commit()

with app.app_context():
    init_db()

def query_db(query, args=(), one=False, commit=False):
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        if commit:
            conn.commit()
            return
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    clients = query_db('SELECT * FROM clients')
    return render_template('index.html', clients=clients)

@app.route('/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        query_db('INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)',
                    (name, email, phone), commit=True)
        return redirect(url_for('index'))
    return render_template('add_client.html')

@app.route('/edit/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        query_db('UPDATE clients SET name=?, email=?, phone=? WHERE id=?',
                    (name, email, phone, client_id), commit=True)
        return redirect(url_for('index'))
    client = query_db('SELECT * FROM clients WHERE id=?', (client_id,), one=True)
    return render_template('edit_client.html', client=client)

@app.route('/delete/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    query_db('DELETE FROM clients WHERE id=?', (client_id,), commit=True)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Enable debug reload in development
    app.run(debug=True)