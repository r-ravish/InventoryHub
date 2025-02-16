from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  sku TEXT,
                  unit TEXT NOT NULL,
                  returnable INTEGER,
                  selling_price REAL,
                  cost_price REAL,
                  tax_rate REAL)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/loading')
def loading():
    return render_template("loading.html")

@app.route('/inventory')
def inventory():
    return render_template("inventory.html")

@app.route('/inventory/add-item', methods=['GET', 'POST'])
def item_form():
    if request.method == 'POST':
        name = request.form['item-name']
        sku = request.form['item-sku']
        unit = request.form['item-unit']
        returnable = 1 if 'returnable' in request.form else 0
        selling_price = request.form['selling-price']
        cost_price = request.form['cost-price']
        tax_rate = request.form['tax-rate']

        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('''INSERT INTO items (name, sku, unit, returnable, selling_price, cost_price, tax_rate)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (name, sku, unit, returnable, selling_price, cost_price, tax_rate))
        conn.commit()
        conn.close()

        return redirect(url_for('inventory'))

    return render_template("item_form.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8000)