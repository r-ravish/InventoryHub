from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy # type: ignore

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50))
    unit = db.Column(db.String(20), nullable=False)
    returnable = db.Column(db.Boolean, default=True)
    selling_price = db.Column(db.Float)
    cost_price = db.Column(db.Float)
    tax_rate = db.Column(db.Float)

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
        returnable = 'returnable' in request.form
        selling_price = float(request.form['selling-price'])
        cost_price = float(request.form['cost-price']) if request.form['cost-price'] else None
        tax_rate = float(request.form['tax-rate']) if request.form['tax-rate'] else None

        new_item = Item(
            name=name,
            sku=sku,
            unit=unit,
            returnable=returnable,
            selling_price=selling_price,
            cost_price=cost_price,
            tax_rate=tax_rate
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for('inventory'))

    return render_template("item_form.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)