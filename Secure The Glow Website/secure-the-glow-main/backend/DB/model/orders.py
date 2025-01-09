import sys
sys.path.append("..") 
from app import ma, db, datetime

# Association table to track multiple products in an order
class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    def __init__(self, order_id, product_id, quantity):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity

# Order model with a relationship to multiple products
class Order(db.Model): 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    customer_email = db.Column(db.String(30), db.ForeignKey('users.email', ondelete='CASCADE'), nullable=False) 
    payment_method = db.Column(db.String(50), nullable=False)
    delivery_time_slot = db.Column(db.String(50), nullable=False)
    date_of_placement = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    delivery_address = db.Column(db.String(255))
    status = db.Column(db.String(50), nullable=False, default="pending")
    
    # Relationship to associate with multiple products
    products = db.relationship('OrderProduct', backref='order', lazy=True, cascade="all, delete-orphan")

    def __init__(self, customer_email, payment_method, delivery_time_slot, delivery_address, status="pending"): 
        super(Order, self).__init__(customer_email=customer_email,
                                    payment_method=payment_method, delivery_time_slot=delivery_time_slot, 
                                    delivery_address=delivery_address, status=status)

# Schemas for nested structure
class OrderProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderProduct
        fields = ("product_id", "quantity")

class OrderSchema(ma.SQLAlchemyAutoSchema): 
    products = ma.Nested(OrderProductSchema, many=True)  # Include products as a nested schema

    class Meta: 
        model = Order 
        fields = ("id", "customer_email", "products", "payment_method", "delivery_time_slot", "date_of_placement", "status", "delivery_address") 

order_schema = OrderSchema()
