from app import app, db
from app.models import Product

# Create some sample products
products = [
    {
        'name': 'Smartphone',
        'price': 599.99,
        'description': 'A high-end smartphone with great features.',
        'image': 'static/images/smartphone.webp'
    },
    {
        'name': 'Laptop',
        'price': 999.99,
        'description': 'A powerful laptop for work and gaming.',
        'image': 'static/images/laptop.webp'
    },
    {
        'name': 'Headphones',
        'price': 199.99,
        'description': 'Noise-cancelling wireless headphones.',
        'image': 'static/images/headphones.webp'
    },
    {
        'name': 'Smartwatch',
        'price': 299.99,
        'description': 'A smartwatch with fitness tracking and notifications.',
        'image': 'static/images/smartwatch.webp'
    },
    {
        'name': 'Tablet',
        'price': 399.99,
        'description': 'A tablet perfect for work and entertainment.',
        'image': 'static/images/tablet.webp'
    }
]

# Wrap the database operations inside the application context
with app.app_context():
    for product in products:
        new_product = Product(
            name=product['name'],
            price=product['price'],
            description=product['description'],
            image=product['image']
        )
        db.session.add(new_product)

    # Commit the changes
    db.session.commit()
    print("Products inserted successfully!")
