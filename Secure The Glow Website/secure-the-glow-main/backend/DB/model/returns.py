from app import ma, db, datetime

class Return(db.Model):
    __tablename__ = 'returns'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)  # Ensure FK to orders
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete="CASCADE"), nullable=False)  # FK to products
    customer_email = db.Column(db.String(255), db.ForeignKey('users.email', ondelete="CASCADE"), nullable=False)  # FK to users
    quantity_to_be_returned= db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='requested', nullable=False)  # requested, approved, denied
    refund_amount = db.Column(db.Float, nullable=True)  # Null until approved
    requested_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    approved_date = db.Column(db.DateTime, nullable=True)
    refund_invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id', ondelete="SET NULL"), nullable=True)  # FK to invoices


    def __init__(self, order_id, product_id, customer_email, quantity, reason=None):
        self.order_id = order_id
        self.product_id = product_id
        self.customer_email = customer_email
        self.quantity = quantity
        self.reason = reason


class ReturnSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Return
        include_fk = True  # Include foreign key fields in the schema
        fields = ("id", "order_id", "product_id", "reason", "status", "refund_amount", "requested_date", "approved_date")


return_schema = ReturnSchema()
returns_schema = ReturnSchema(many=True)
