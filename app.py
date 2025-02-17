# from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
# from sqlalchemy import func, case
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config["SECRET_KEY"] = "welcome"
# db = SQLAlchemy(app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# class User(db.Model, UserMixin):
#     __tablename__ = "user"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100))
#     email = db.Column(db.String(100))
#     password_hash = db.Column(db.String(200))
#     phone = db.Column(db.String(20))
#     country = db.Column(db.String(100))
#     state = db.Column(db.String(100))
#     role = db.Column(db.String(100), default="user")
#     last_login = db.Column(db.DateTime, default=datetime.utcnow)

#     def generate_password(self, simple_password):
#         self.password_hash = generate_password_hash(simple_password)
    
#     def check_password(self, simple_password):
#         return check_password_hash(self.password_hash, simple_password)

# class Item(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     sku = db.Column(db.String(50))
#     unit = db.Column(db.String(20), nullable=False)
#     returnable = db.Column(db.Boolean, default=True)
#     selling_price = db.Column(db.Float)
#     cost_price = db.Column(db.Float)
#     tax_rate = db.Column(db.Float)
#     quantity_in_hand = db.Column(db.Integer, default=0)
#     quantity_to_receive = db.Column(db.Integer, default=0)
#     reorder_point = db.Column(db.Integer, default=10)

# @app.route("/register", methods=["POST","GET"])
# def registerFunction():
#     if request.method=="POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         phone = request.form.get("phone")
#         country = request.form.get("country")
#         state = request.form.get("state")

#         if User.query.filter_by(email=email).first():
#             flash("User already exists")
#             return redirect(url_for("home"))

#         user_object = User(
#             username=username,
#             email=email,
#             phone=phone,
#             country=country,
#             state=state
#         )
#         user_object.generate_password(password)
#         db.session.add(user_object)
#         db.session.commit()

#         flash("User registered successfully.")
#         return redirect(url_for("loginFunction"))

#     return render_template("signup.html")

# @app.route("/login",methods=["POST","GET"])
# def loginFunction():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")
#         user_object = User.query.filter_by(email=email).first()

#         if user_object and user_object.check_password(password):
#             login_user(user_object)
#             user_object.last_login = datetime.utcnow()  # Update last login time
#             db.session.commit()
#             flash("User logged in successfully.")
#             return redirect(url_for("profile"))  # Redirect to profile page after login
#         else:
#             flash("Invalid email or password.")
#             return redirect(url_for("loginFunction"))

#     return render_template("login.html")

# @login_manager.user_loader
# def load_user(user_id):
#     return db.session.get(User,int(user_id))

# def role_required(role):
#     def decorator(func):
#         def wrapper(args,*kwargs):
#             if current_user.role!=role:
#                 flash("Unauthorised Access")
#                 return redirect(url_for("loginFunction"))
#             return func(args,*kwargs)
#         return wrapper
#     return decorator

# @app.route("/logout")
# def logout():
#     logout_user()
#     flash("User Logged Out Successfully")
#     return redirect(url_for("home"))

# with app.app_context():
#     db.create_all()

#     if not User.query.filter_by(role="admin").first():
#         admin=User(username="admin" ,email="admin@gmail.com" ,role="admin")
#         admin.generate_password("admin")
#         db.session.add(admin)
#         db.session.commit()

# @app.route('/')
# def home():
#     return render_template("index.html")
   

# @app.route('/dashboard')
# def dashboard():
#     # Inventory Value Metrics
#     total_items = Item.query.count()
    
#     # Use coalesce to handle NULL values in cost_price calculation
#     total_inventory_value = db.session.query(
#         func.sum(
#             case(
#                 (Item.cost_price.isnot(None), Item.quantity_in_hand * Item.cost_price),
#                 else_=0
#             )
#         )
#     ).scalar() or 0
    
#     avg_item_value = total_inventory_value / total_items if total_items > 0 else 0
    
#     # Stock Status
#     low_stock_items = Item.query.filter(Item.quantity_in_hand <= Item.reorder_point).count()
#     out_of_stock_items = Item.query.filter(Item.quantity_in_hand == 0).count()
#     items_to_receive = Item.query.filter(Item.quantity_to_receive > 0).count()
    
#     # Value Analysis - only count items with non-null cost_price
#     high_value_items = Item.query.filter(
#         Item.cost_price.isnot(None),
#         Item.cost_price > 1000
#     ).count()
    
#     # Returnable Status
#     returnable_items = Item.query.filter_by(returnable=True).count()
#     non_returnable_items = Item.query.filter_by(returnable=False).count()
    
#     # Top Items by Value - only get items with non-null cost_price
#     top_value_items = Item.query.filter(
#         Item.cost_price.isnot(None)
#     ).order_by(Item.cost_price.desc()).limit(5).all()
    
#     # Items by Tax Rate - handle null tax_rates
#     tax_distribution = db.session.query(
#         case(
#             (Item.tax_rate.is_(None), 0),
#             else_=Item.tax_rate
#         ).label('tax_rate'),
#         func.count(Item.id).label('count')
#     ).group_by(
#         case(
#             (Item.tax_rate.is_(None), 0),
#             else_=Item.tax_rate
#         )
#     ).all()
    
#     # Calculate profit margins - only for items with both prices
#     items_with_margins = Item.query.filter(
#         Item.selling_price.isnot(None),
#         Item.cost_price.isnot(None),
#         Item.cost_price > 0  # Prevent division by zero
#     ).all()
    
#     margin_data = []
#     for item in items_with_margins:
#         margin = ((item.selling_price - item.cost_price) / item.cost_price * 100)
#         margin_data.append({
#             'name': item.name,
#             'margin': round(margin, 2)
#         })
    
#     # Sort by margin and get top 5
#     margin_data.sort(key=lambda x: x['margin'], reverse=True)
#     top_margin_items = margin_data[:5]

#     return render_template(
#         "dashboard.html",
#         total_items=total_items,
#         total_inventory_value=total_inventory_value,
#         avg_item_value=avg_item_value,
#         low_stock_items=low_stock_items,
#         out_of_stock_items=out_of_stock_items,
#         items_to_receive=items_to_receive,
#         high_value_items=high_value_items,
#         returnable_items=returnable_items,
#         non_returnable_items=non_returnable_items,
#         top_value_items=top_value_items,
#         tax_distribution=tax_distribution,
#         top_margin_items=top_margin_items,
#         show_sidebar=True
#     )

# @app.route('/inventory')
# def inventory():
#     return render_template("inventory.html",show_sidebar=True)


# @app.route('/inventory/add-item', methods=['GET', 'POST'])
# def item_form():
#     if request.method == 'POST':
#         name = request.form['item-name']
#         sku = request.form['item-sku']
#         unit = request.form['item-unit']
#         returnable = 'returnable' in request.form
#         selling_price = float(request.form['selling-price'])
#         cost_price = float(request.form['cost-price']) if request.form['cost-price'] else None
#         tax_rate = float(request.form['tax-rate']) if request.form['tax-rate'] else None

#         new_item = Item(
#             name=name,
#             sku=sku,
#             unit=unit,
#             returnable=returnable,
#             selling_price=selling_price,
#             cost_price=cost_price,
#             tax_rate=tax_rate
#         )

#         db.session.add(new_item)
#         db.session.commit()

#         return redirect(url_for('inventory'))

#     return render_template("item_form.html",show_sidebar=True)

# @app.route('/profile')
# @login_required
# def profile():
#     return render_template("profile.html", user=current_user)


# # @app.route('/delete-data', methods=['GET', 'POST'])
# # def delete_data():
# #     db.drop_all()
# #     db.create_all()
# #     flash("All data has been deleted and database has been reset.")
# #     return redirect(url_for('dashboard'))


# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True, port=8000)


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

# User Model
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

# Item Model
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

# Authentication routes
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
            flash("User already exists")
            return redirect(url_for("home"))

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

        flash("User registered successfully.")
        return redirect(url_for("loginFunction"))

    return render_template("signup.html")

@app.route("/login",methods=["POST","GET"])
def loginFunction():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_object = User.query.filter_by(email=email).first()

        if user_object and user_object.check_password(password):
            login_user(user_object)
            user_object.last_login = datetime.utcnow()
            db.session.commit()
            # flash("User logged in successfully.")
            return redirect(url_for("profile"))
        else:
            # flash("Invalid email or password.")
            return redirect(url_for("loginFunction"))

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
    # flash("User Logged Out Successfully")
    return redirect(url_for("loginFunction"))

# Main routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    # Inventory Value Metrics
    total_items = Item.query.count()
    
    total_inventory_value = db.session.query(
        func.sum(
            case(
                (Item.cost_price.isnot(None), Item.quantity_in_hand * Item.cost_price),
                else_=0
            )
        )
    ).scalar() or 0
    
    avg_item_value = total_inventory_value / total_items if total_items > 0 else 0
    
    # Stock Status
    low_stock_items = Item.query.filter(Item.quantity_in_hand <= Item.reorder_point).count()
    out_of_stock_items = Item.query.filter(Item.quantity_in_hand == 0).count()
    items_to_receive = Item.query.filter(Item.quantity_to_receive > 0).count()
    
    high_value_items = Item.query.filter(
        Item.cost_price.isnot(None),
        Item.cost_price > 1000
    ).count()
    
    returnable_items = Item.query.filter_by(returnable=True).count()
    non_returnable_items = Item.query.filter_by(returnable=False).count()
    
    top_value_items = Item.query.filter(
        Item.cost_price.isnot(None)
    ).order_by(Item.cost_price.desc()).limit(5).all()
    
    tax_distribution = db.session.query(
        case(
            (Item.tax_rate.is_(None), 0),
            else_=Item.tax_rate
        ).label('tax_rate'),
        func.count(Item.id).label('count')
    ).group_by(
        case(
            (Item.tax_rate.is_(None), 0),
            else_=Item.tax_rate
        )
    ).all()
    
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

@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Verify current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('change_password'))

        # Validate new password
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('change_password'))

        # Ensure new password is different from current
        if current_password == new_password:
            flash('New password must be different from current password', 'error')
            return redirect(url_for('change_password'))

        # Update password
        current_user.generate_password(new_password)
        db.session.commit()

        flash('Password updated successfully', 'success')
        return redirect(url_for('profile'))

    return render_template("change_password.html", user=current_user)


# Item CRUD routes
@app.route('/items')
def item_list():
    items = Item.query.all()
    total_items = len(items)
    total_value = sum(item.selling_price for item in items if item.selling_price)
    item_types = {
        "Goods": Item.query.count()
    }
    
    return render_template(
        "item_list.html",
        items=items,
        total_items=total_items,
        total_value=total_value,
        item_types=item_types,
        show_sidebar=True
    )

@app.route('/items/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully', 'success')
    return redirect(url_for('item_list'))

@app.route('/items/update/<int:item_id>', methods=['POST'])
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
    flash('Item updated successfully', 'success')
    return redirect(url_for('item_list'))

# Database initialization
with app.app_context():
    db.create_all()

    if not User.query.filter_by(role="admin").first():
        admin=User(username="admin" ,email="admin@gmail.com" ,role="admin")
        admin.generate_password("admin")
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True, port=8000)