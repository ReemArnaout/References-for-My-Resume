import sys
sys.path.append("..")
from app import ma, db, datetime

class InvoiceProduct(db.Model):
    __tablename__ = 'invoice_product'
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id', ondelete='CASCADE'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time_of_purchase = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    # Relationships
    product = db.relationship('Product', backref=db.backref('invoice_products', lazy=True, cascade="all, delete-orphan"))

class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False, unique=True)
    invoice_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(db.String(50), nullable=False, default="unpaid")

    # Relationship to Order
    order = db.relationship('Order', backref=db.backref('invoice', uselist=False, cascade="all, delete"))
    products = db.relationship('InvoiceProduct', lazy=True)  # Remove backref here

    def __init__(self, order_id, total_amount, tax=0.0, payment_status="unpaid"):
        self.order_id = order_id
        self.total_amount = total_amount
        self.tax = tax
        self.payment_status = payment_status


class InvoiceProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InvoiceProduct
        fields = ("product_id", "quantity", "price_at_time_of_purchase", "total_price")
    
    # Optionally, you can include details from the Product model
    product = ma.Nested('ProductSchema')  # Assuming you have a Product schema


class InvoiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Invoice
        fields = ("id", "order_id", "invoice_date", "total_amount", "tax", "payment_status", "invoice_products")

    # Nested InvoiceProductSchema to include product details
    invoice_products = ma.Nested('InvoiceProductSchema', many=True)


invoice_schema = InvoiceSchema()
invoices_schema = InvoiceSchema(many=True)
