from flask import render_template, redirect, url_for, flash, request, session
from app import app, db, bcrypt
from app.models import User, Product
from flask_login import login_user, logout_user, current_user, login_required
import stripe


# Home Route - Display Products
@app.route('/')
@app.route('/home')
def home():
    products = Product.query.all()  # Retrieve all products from the database
    return render_template('home.html', products=products)


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=request.form['username'], email=request.form['email'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')


# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))


# Cart Route
@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', [])
    products = [Product.query.get(item_id) for item_id in cart_items]

    # Calculate total price
    total_price = sum(product.price for product in products)

    return render_template('cart.html', products=products, total_price=total_price)


# Add to Cart Route
@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    # Ensure that the cart is always a list
    cart = session.get('cart', [])

    # If the cart was mistakenly stored as a dict, reset it to an empty list
    if not isinstance(cart, list):
        cart = []

    # Add the product ID to the cart list
    cart.append(product_id)

    # Save the updated cart back to the session
    session['cart'] = cart

    flash(f'Added {product.name} to your cart!', 'success')
    return redirect(url_for('home'))


# Remove from Cart Route
@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', [])

    # Ensure the cart is a list and check if the product exists in the cart
    if isinstance(cart, list) and product_id in cart:
        cart.remove(product_id)
        session['cart'] = cart  # Update the session cart
        flash('Product removed from your cart.', 'info')

    return redirect(url_for('cart'))



# Checkout Route with Stripe
@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = session.get('cart', [])
    if not cart:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('home'))

    line_items = []
    for product_id in cart:
        product = Product.query.get(product_id)
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100),  # Stripe uses cents
            },
            'quantity': 1,
        })

    session_stripe = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=url_for('success', _external=True),
        cancel_url=url_for('cancel', _external=True),
    )
    return redirect(session_stripe.url, code=303)


# Payment Success Route
@app.route('/success')
def success():
    session.pop('cart', None)  # Clear the cart after successful payment
    flash('Payment successful!', 'success')
    return render_template('success.html')


# Payment Cancel Route
@app.route('/cancel')
def cancel():
    flash('Payment was cancelled', 'warning')
    return render_template('cancel.html')
