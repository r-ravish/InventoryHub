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

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'goods' or 'service'
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    returnable = db.Column(db.Boolean, default=False)
    unit = db.Column(db.String(50), nullable=False)
    manufacturer = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # For storing attributes and options
    attributes = db.relationship('GroupAttribute', backref='group', cascade='all, delete-orphan')

class GroupAttribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    attribute_name = db.Column(db.String(100), nullable=False)
    options = db.Column(db.Text, nullable=False)  # Store as comma-separated values

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
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_object = User.query.filter_by(email=email).first()

        if user_object and user_object.check_password(password):
            login_user(user_object)
            user_object.last_login = datetime.utcnow()
            db.session.commit()
            flash(f"Welcome back, {user_object.username}!", "success")
            return redirect(url_for("home"))
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

@app.route('/about')
def about():
    return render_template("about_us.html")


# @app.route('/dashboard')
# @login_required
# def dashboard():
#     flash(f"Welcome to your dashboard, {current_user.username}!", "info")
    
#     # Existing queries
#     total_items = Item.query.count()
#     total_inventory_value = db.session.query(
#         func.sum(case((Item.cost_price.isnot(None), 
#                       Item.quantity_in_hand * Item.cost_price), else_=0))
#     ).scalar() or 0
    
#     avg_item_value = total_inventory_value / total_items if total_items > 0 else 0
#     low_stock_items = Item.query.filter(Item.quantity_in_hand <= Item.reorder_point).count()
#     out_of_stock_items = Item.query.filter(Item.quantity_in_hand == 0).count()
#     items_to_receive = Item.query.filter(Item.quantity_to_receive > 0).count()
#     high_value_items = Item.query.filter(Item.cost_price.isnot(None), 
#                                        Item.cost_price > 1000).count()
#     returnable_items = Item.query.filter_by(returnable=True).count()
#     non_returnable_items = Item.query.filter_by(returnable=False).count()

#     # New Group-related queries
#     total_groups = Group.query.count()
#     goods_groups = Group.query.filter_by(type='goods').count()
#     service_groups = Group.query.filter_by(type='service').count()
#     returnable_groups = Group.query.filter_by(returnable=True).count()
    
#     # Recently created groups
#     recent_groups = Group.query.order_by(Group.created_at.desc()).limit(5).all()
    
#     # Groups by manufacturer
#     manufacturer_distribution = db.session.query(
#         Group.manufacturer,
#         func.count(Group.id).label('count')
#     ).group_by(Group.manufacturer).all()
    
#     # Groups by unit
#     unit_distribution = db.session.query(
#         Group.unit,
#         func.count(Group.id).label('count')
#     ).group_by(Group.unit).all()
    
#     # Groups with most attributes
#     groups_with_attributes = db.session.query(
#         Group,
#         func.count(GroupAttribute.id).label('attribute_count')
#     ).join(GroupAttribute).group_by(Group.id)\
#     .order_by(func.count(GroupAttribute.id).desc())\
#     .limit(5).all()
    
#     # Brand distribution
#     brand_distribution = db.session.query(
#         Group.brand,
#         func.count(Group.id).label('count')
#     ).filter(Group.brand.isnot(None))\
#     .group_by(Group.brand)\
#     .order_by(func.count(Group.id).desc())\
#     .limit(5).all()

#     # Get the sort parameter from URL
#     sort_by = request.args.get('sort', 'created_at')
#     sort_order = request.args.get('order', 'desc')
    
#     # Base query for groups
#     groups_query = Group.query
    
#     # Apply filters if provided
#     type_filter = request.args.get('type')
#     if type_filter:
#         groups_query = groups_query.filter(Group.type == type_filter)
        
#     returnable_filter = request.args.get('returnable')
#     if returnable_filter:
#         groups_query = groups_query.filter(Group.returnable == (returnable_filter == 'true'))
        
#     manufacturer_filter = request.args.get('manufacturer')
#     if manufacturer_filter:
#         groups_query = groups_query.filter(Group.manufacturer == manufacturer_filter)
    
#     # Apply sorting
#     if sort_by == 'name':
#         groups_query = groups_query.order_by(Group.name.desc() if sort_order == 'desc' else Group.name)
#     elif sort_by == 'created_at':
#         groups_query = groups_query.order_by(Group.created_at.desc() if sort_order == 'desc' else Group.created_at)
    
#     # Execute the query
#     filtered_groups = groups_query.all()
    
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
#         # New group-related variables
#         total_groups=total_groups,
#         goods_groups=goods_groups,
#         service_groups=service_groups,
#         returnable_groups=returnable_groups,
#         recent_groups=recent_groups,
#         manufacturer_distribution=manufacturer_distribution,
#         unit_distribution=unit_distribution,
#         groups_with_attributes=groups_with_attributes,
#         brand_distribution=brand_distribution,
#         filtered_groups=filtered_groups,
#         show_sidebar=True
#     )

@app.route('/dashboard')
@login_required
def dashboard():
    flash(f"Welcome to your dashboard, {current_user.username}!", "info")
    
    # Base metrics
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

    # Top items by value
    top_value_items = db.session.query(Item)\
        .filter(Item.cost_price.isnot(None), Item.quantity_in_hand > 0)\
        .order_by((Item.cost_price * Item.quantity_in_hand).desc())\
        .limit(5).all()

    # Top items by margin
    # Assuming selling_price and cost_price are columns in your Item model
    top_margin_items = db.session.query(
        Item,
        ((Item.selling_price - Item.cost_price) / Item.cost_price * 100).label('margin')
    ).filter(
        Item.cost_price.isnot(None),
        Item.selling_price.isnot(None),
        Item.cost_price > 0
    ).order_by(((Item.selling_price - Item.cost_price) / Item.cost_price).desc())\
    .limit(5).all()

    # Tax rate distribution
    tax_distribution = db.session.query(
        Item.tax_rate,
        func.count(Item.id).label('count')
    ).group_by(Item.tax_rate)\
    .order_by(Item.tax_rate)\
    .all()

    # Group metrics with filters
    type_filter = request.args.get('typeFilter')
    returnable_filter = request.args.get('returnableFilter')
    sort_by = request.args.get('sortBy', 'created_at')
    sort_order = request.args.get('sortOrder', 'desc')

    groups_query = Group.query

    if type_filter:
        groups_query = groups_query.filter(Group.type == type_filter)
    
    if returnable_filter:
        returnable_value = returnable_filter.lower() == 'true'
        groups_query = groups_query.filter(Group.returnable == returnable_value)

    # Apply sorting
    if sort_by == 'name':
        order_column = Group.name
    else:  # default to created_at
        order_column = Group.created_at
    
    if sort_order == 'desc':
        groups_query = groups_query.order_by(order_column.desc())
    else:
        groups_query = groups_query.order_by(order_column.asc())

    # Get group metrics
    total_groups = groups_query.count()
    goods_groups = groups_query.filter_by(type='goods').count()
    service_groups = groups_query.filter_by(type='service').count()
    returnable_groups = groups_query.filter_by(returnable=True).count()
    recent_groups = groups_query.limit(5).all()

    # Unit distribution
    unit_distribution = db.session.query(
        Group.unit,
        func.count(Group.id).label('count')
    ).group_by(Group.unit).all()

    # Groups with attributes
    groups_with_attributes = db.session.query(
        Group,
        func.count(GroupAttribute.id).label('attribute_count')
    ).join(GroupAttribute).group_by(Group.id)\
    .order_by(func.count(GroupAttribute.id).desc())\
    .limit(5).all()

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
        top_margin_items=top_margin_items,
        tax_distribution=tax_distribution,
        total_groups=total_groups,
        goods_groups=goods_groups,
        service_groups=service_groups,
        returnable_groups=returnable_groups,
        recent_groups=recent_groups,
        unit_distribution=unit_distribution,
        groups_with_attributes=groups_with_attributes,
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
@admin_required
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


# Add to your app.py



@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # User statistics
    total_users = User.query.count()
    admin_users = User.query.filter_by(role="admin").count()
    regular_users = User.query.filter_by(role="user").count()
    
    # Get recent users with formatted dates
    recent_users = [
        {
            'username': user.username,
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S'),
            'email': user.email,
            'country': user.country
        }
        for user in User.query.order_by(User.last_login.desc()).limit(5).all()
    ]
    
    # Inventory statistics
    total_items = Item.query.count()
    total_inventory_value = db.session.query(
        func.sum(case((Item.cost_price.isnot(None), 
                      Item.quantity_in_hand * Item.cost_price), else_=0))
    ).scalar() or 0
    
    # Stock alerts
    low_stock_items = Item.query.filter(Item.quantity_in_hand <= Item.reorder_point).count()
    out_of_stock_items = Item.query.filter(Item.quantity_in_hand == 0).count()
    
    # Get high value items
    high_value_items = [
        {
            'name': item.name,
            'cost_price': float(item.cost_price) if item.cost_price else 0,
            'quantity': item.quantity_in_hand
        }
        for item in Item.query.filter(
            Item.cost_price.isnot(None)
        ).order_by(Item.cost_price.desc()).limit(5).all()
    ]
    
    # User activity by country
    user_by_country = [
        {
            'country': country or 'Not Specified',
            'count': count
        }
        for country, count in db.session.query(
            User.country,
            func.count(User.id).label('count')
        ).group_by(User.country).all()
    ]
    
    # Price distribution
    price_ranges = [
        (0, 100, '0-100'),
        (101, 500, '101-500'),
        (501, 1000, '501-1000'),
        (1001, float('inf'), '1000+')
    ]
    
    price_distribution = []
    for min_price, max_price, label in price_ranges:
        count = Item.query.filter(
            Item.selling_price >= min_price,
            Item.selling_price <= max_price if max_price != float('inf') else Item.selling_price > min_price
        ).count()
        price_distribution.append({'range': label, 'count': count})

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        admin_users=admin_users,
        regular_users=regular_users,
        recent_users=recent_users,
        total_items=total_items,
        total_inventory_value=total_inventory_value,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        high_value_items=high_value_items,
        user_by_country=user_by_country,
        price_distribution=price_distribution
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




@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    if request.method == 'POST':
        try:
            new_group = Group(
                type=request.form.get('type'),
                name=request.form.get('itemGroupName'),
                description=request.form.get('description'),
                returnable='returnable' in request.form,
                unit=request.form.get('unit'),
                manufacturer=request.form.get('manufacturer'),
                brand=request.form.get('brand'),
                created_by=current_user.id
            )
            
            db.session.add(new_group)
            db.session.flush()  
            
            if 'createAttributes' in request.form:
                attributes = request.form.getlist('attribute[]')
                options = request.form.getlist('options[]')
                
                for attr, opt in zip(attributes, options):
                    if attr and opt:  
                        group_attr = GroupAttribute(
                            group_id=new_group.id,
                            attribute_name=attr,
                            options=opt
                        )
                        db.session.add(group_attr)
            
            if 'images[]' in request.files:
                files = request.files.getlist('images[]')
                # File handling logic here if needed
            
            db.session.commit()
            flash(f"Item group '{request.form.get('itemGroupName')}' has been added successfully!", "success")
            return redirect(url_for('inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding item group: {str(e)}", "error")
            return render_template('group_form.html', show_sidebar=True)
    
    return render_template('group_form.html', show_sidebar=True)


with app.app_context():
    db.create_all()

    if not User.query.filter_by(role="admin").first():
        admin = User(username="admin", email="admin@gmail.com", role="admin")
        admin.generate_password("admin")
        db.session.add(admin)
        db.session.commit()



if __name__ == "__main__":
       app.run(debug=True, port=8000)