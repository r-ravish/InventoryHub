from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from sqlalchemy import func, case
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "welcome"
db = SQLAlchemy(app)

# Updated Login Manager Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "loginFunction"
login_manager.login_message = "Please login to access this page."
login_manager.login_message_category = "error"

@login_manager.unauthorized_handler
def unauthorized():
    flash("Please login to access this page.", "error")
    return redirect(url_for('loginFunction'))

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    country = db.Column(db.String(100))
    state = db.Column(db.String(100))
    role = db.Column(db.String(100), default="user")
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login to access this page.", "error")
            return redirect(url_for("loginFunction"))
        if current_user.role != "admin":
            flash("Access denied: Admin privileges required for this operation.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/register", methods=["POST","GET"])
def registerFunction():
    if request.method=="POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        country = request.form.get("country")
        state = request.form.get("state")

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please use a different email.", "error")
            return redirect(url_for("registerFunction"))

        user_object = User(
            username=username,
            email=email,
            phone=phone,
            country=country,
            state=state
        )
        user_object.generate_password(password)
        db.session.add(user_object)
        db.session.commit()

        flash("Registration successful! Please login to continue.", "success")
        return redirect(url_for("loginFunction"))

    return render_template("signup.html")

@app.route("/login",methods=["POST","GET"])
def loginFunction():
    if current_user.is_authenticated:
        flash("You are already logged in!", "info")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_object = User.query.filter_by(email=email).first()

        if user_object and user_object.check_password(password):
            login_user(user_object)
            user_object.last_login = datetime.utcnow()
            db.session.commit()
            flash(f"Welcome back, {user_object.username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for("loginFunction"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        flash(f"Goodbye, {current_user.username}! You have been logged out.", "success")
        logout_user()
    return redirect(url_for("loginFunction"))

@app.route('/')
def home():
    company_name = "InventoryHub"
    return render_template("index.html", 
                         user=current_user, 
                         company_name=company_name,
                         is_authenticated=current_user.is_authenticated)

@app.route('/dashboard')
@login_required
def dashboard():
    flash(f"Welcome to your dashboard, {current_user.username}!", "info")
    
    total_items = Item.query.count()
    total_inventory_value = db.session.query(
        func.sum(case((Item.cost_price.isnot(None), 
                      Item.quantity_in_hand * Item.cost_price), else_=0))
    ).scalar() or 0
    
    avg_item_value = total_inventory_value / total_items if total_items > 0 else 0
    low_stock_items = Item.query.filter(Item.quantity_in_hand <= Item.reorder_point).count()
    out_of_stock_items = Item.query.filter(Item.quantity_in_hand == 0).count()
    items_to_receive = Item.query.filter(Item.quantity_to_receive > 0).count()
    high_value_items = Item.query.filter(Item.cost_price.isnot(None), 
                                       Item.cost_price > 1000).count()
    returnable_items = Item.query.filter_by(returnable=True).count()
    non_returnable_items = Item.query.filter_by(returnable=False).count()
    
    top_value_items = Item.query.filter(Item.cost_price.isnot(None))\
        .order_by(Item.cost_price.desc()).limit(5).all()
    
    tax_distribution = db.session.query(
        case((Item.tax_rate.is_(None), 0), else_=Item.tax_rate).label('tax_rate'),
        func.count(Item.id).label('count')
    ).group_by(case((Item.tax_rate.is_(None), 0), else_=Item.tax_rate)).all()
    
    items_with_margins = Item.query.filter(
        Item.selling_price.isnot(None),
        Item.cost_price.isnot(None),
        Item.cost_price > 0
    ).all()
    
    margin_data = []
    for item in items_with_margins:
        margin = ((item.selling_price - item.cost_price) / item.cost_price * 100)
        margin_data.append({
            'name': item.name,
            'margin': round(margin, 2)
        })
    
    margin_data.sort(key=lambda x: x['margin'], reverse=True)
    top_margin_items = margin_data[:5]

    return render_template(
        "dashboard.html",
        total_items=total_items,
        total_inventory_value=total_inventory_value,
        avg_item_value=avg_item_value,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        items_to_receive=items_to_receive,
        high_value_items=high_value_items,
        returnable_items=returnable_items,
        non_returnable_items=non_returnable_items,
        top_value_items=top_value_items,
        tax_distribution=tax_distribution,
        top_margin_items=top_margin_items,
        show_sidebar=True
    )

@app.route('/inventory')
@login_required
def inventory():
    flash("Viewing inventory management section.", "info")
    return render_template("inventory.html", show_sidebar=True)

@app.route('/inventory/add-item', methods=['GET', 'POST'])
@login_required
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
        flash(f"Item '{name}' has been added successfully!", "success")
        return redirect(url_for('inventory'))

    return render_template("item_form.html", show_sidebar=True)

@app.route('/profile')
@login_required
def profile():
    flash("Viewing your profile information.", "info")
    return render_template("profile.html", user=current_user)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect. Please try again.', 'error')
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match. Please try again.', 'error')
            return redirect(url_for('change_password'))

        if current_password == new_password:
            flash('New password must be different from current password.', 'error')
            return redirect(url_for('change_password'))

        current_user.generate_password(new_password)
        db.session.commit()
        flash('Your password has been updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template("change_password.html", user=current_user)

@app.route('/items')
@login_required
def item_list():
    items = Item.query.all()
    total_items = len(items)
    total_value = sum(item.selling_price for item in items if item.selling_price)
    item_types = {
        "Goods": Item.query.count()
    }
    
    flash(f"Viewing list of {total_items} items.", "info")
    return render_template(
        "item_list.html",
        items=items,
        total_items=total_items,
        total_value=total_value,
        item_types=item_types,
        show_sidebar=True
    )

@app.route('/items/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    item_name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f"Item '{item_name}' has been deleted successfully.", "success")
    return redirect(url_for('item_list'))

@app.route('/items/update/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if request.form.get('name'):
        item.name = request.form.get('name')
    if request.form.get('sku'):
        item.sku = request.form.get('sku')
    if request.form.get('unit'):
        item.unit = request.form.get('unit')
    if request.form.get('quantity_in_hand'):
        item.quantity_in_hand = int(request.form.get('quantity_in_hand'))
    if request.form.get('reorder_point'):
        item.reorder_point = int(request.form.get('reorder_point'))
    if request.form.get('selling_price'):
        item.selling_price = float(request.form.get('selling_price'))
    if request.form.get('cost_price'):
        item.cost_price = float(request.form.get('cost_price'))
    if request.form.get('tax_rate'):
        item.tax_rate = float(request.form.get('tax_rate'))
    
    item.returnable = 'returnable' in request.form
    
    db.session.commit()
    flash(f"Item '{item.name}' has been updated successfully!", "success")
    return redirect(url_for('item_list'))

with app.app_context():
    db.create_all()

    if not User.query.filter_by(role="admin").first():
        admin = User(username="admin", email="admin@gmail.com", role="admin")
        admin.generate_password("admin")
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
       app.run(debug=True, port=8000)