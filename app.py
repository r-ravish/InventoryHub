from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from sqlalchemy import func, case
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "welcome"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    _tablename_ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(100), default="user")

    def generate_password(self, simple_password):
        self.password_hash = generate_password_hash(simple_password)
    
    def check_password(self, simple_password):
        return check_password_hash(self.password_hash, simple_password)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50))
    unit = db.Column(db.String(20), nullable=False)
    returnable = db.Column(db.Boolean, default=True)
    selling_price = db.Column(db.Float)
    cost_price = db.Column(db.Float)
    tax_rate = db.Column(db.Float)
    quantity_in_hand = db.Column(db.Integer, default=0)
    quantity_to_receive = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=10)

class SalesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(50))
    status = db.Column(db.String(20))  # draft, confirmed, packed, shipped, invoiced
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    item = db.relationship('Item', backref='sales_orders')

@app.route("/register", methods=["POST","GET"])
def registerFunction():
    if request.method=="POST":
        username=request.form.get("username")
        email=request.form.get("email")
        password=request.form.get("password")
        # phone=request.form.get("phone")
        # role=request.form.get("role")

        if User.query.filter_by(email=email).first():
            flash("User already exists")
            return redirect(url_for("home"))

        user_object=User(username=username,email=email)
        user_object.generate_password(password)
        db.session.add(user_object)
        db.session.commit()

        flash("User registered successfully.")
        return redirect(url_for("loginFunction"))

    return render_template("signup.html")

@app.route("/login",methods=["POST","GET"])
def loginFunction():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        # role=request.form.get("role")
        user_object=User.query.filter_by(email=email).first()

        if user_object and user_object.check_password(password):
            login_user(user_object)
            flash("User logged in successfully.")
            return redirect(url_for("home"))
            # return("succesfull login")
        else:
            return "Invalid User"
            
    return render_template("login.html")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))

def role_required(role):
    def decorator(func):
        def wrapper(args,*kwargs):
            if current_user.role!=role:
                flash("Unauthorised Access")
                return redirect(url_for("loginFunction"))
            return func(args,*kwargs)
        return wrapper
    return decorator

@app.route("/logout")
def logout():
    logout_user()
    flash("User Logged Out Successfully")
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()

    if not User.query.filter_by(role="admin").first():
        admin=User(username="admin" ,email="admin@gmail.com" ,role="admin")
        admin.generate_password("admin")
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return render_template("index.html")
   


@app.route('/dashboard')
def dashboard():
     # Sales Activity Metrics
    to_be_packed = SalesOrder.query.filter_by(status='confirmed').count()
    to_be_shipped = SalesOrder.query.filter_by(status='packed').count()
    to_be_delivered = SalesOrder.query.filter_by(status='shipped').count()
    to_be_invoiced = SalesOrder.query.filter_by(status='delivered').count()

    # Inventory Summary
    total_quantity = db.session.query(func.sum(Item.quantity_in_hand)).scalar() or 0
    to_be_received = db.session.query(func.sum(Item.quantity_to_receive)).scalar() or 0

    # Product Details
    low_stock_items = Item.query.filter(Item.quantity_in_hand <= Item.reorder_point).count()
    all_items = Item.query.count()
    active_items_percentage = 78  # This could be calculated based on your business logic

    # Top Selling Items
    top_selling = db.session.query(
        Item,
        func.count(SalesOrder.id).label('total_sales')
    ).join(SalesOrder).group_by(Item.id).order_by(func.count(SalesOrder.id).desc()).limit(3).all()

    # Sales Order Statistics
    # Sales Order Statistics
    sales_stats = db.session.query(
        SalesOrder.channel,
        func.count(case((SalesOrder.status == 'draft', 1))).label('draft'),
        func.count(case((SalesOrder.status == 'confirmed', 1))).label('confirmed'),
        func.count(case((SalesOrder.status == 'packed', 1))).label('packed'),
        func.count(case((SalesOrder.status == 'shipped', 1))).label('shipped'),
        func.count(case((SalesOrder.status == 'invoiced', 1))).label('invoiced')
    ).group_by(SalesOrder.channel).first()


    return render_template(
        "dashboard.html",
        to_be_packed=to_be_packed,
        to_be_shipped=to_be_shipped,
        to_be_delivered=to_be_delivered,
        to_be_invoiced=to_be_invoiced,
        total_quantity=total_quantity,
        to_be_received=to_be_received,
        low_stock_items=low_stock_items,
        all_items=all_items,
        active_items_percentage=active_items_percentage,
        top_selling=top_selling,
        sales_stats=sales_stats,show_sidebar=True
    )




@app.route('/inventory')
def inventory():
    return render_template("inventory.html",show_sidebar=True)


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

    return render_template("item_form.html",show_sidebar=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)





