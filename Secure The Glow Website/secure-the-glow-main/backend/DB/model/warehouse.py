import sys
sys.path.append("..") 
from app import ma, db

# Association table to track multiple products in a warehouse
class WarehouseProduct(db.Model):
    __tablename__ = 'warehouse_product'
    __table_args__ = {'extend_existing': True}  # Allow redefinition if already exists
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.warehouse_id'), primary_key=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, warehouse_id, product_id, quantity):
        self.warehouse_id = warehouse_id
        self.product_id = product_id
        self.quantity = quantity

# Warehouse model with a relationship to multiple products
class Warehouse(db.Model):   
    warehouse_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    warehouse_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    
    # Relationship to associate with multiple products
    products = db.relationship('WarehouseProduct', backref='warehouse', lazy=True, cascade="all, delete-orphan")

    def __init__(self, warehouse_name, location):
        self.warehouse_name = warehouse_name
        self.location = location

# Schemas for nested structure
class WarehouseProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WarehouseProduct
        fields = ("product_id", "quantity")

class WarehouseSchema(ma.SQLAlchemyAutoSchema):
    products = ma.Nested(WarehouseProductSchema, many=True)  # Include products as a nested schema

    class Meta:
        model = Warehouse
        fields = ("warehouse_id", "warehouse_name", "location", "products")

# Schema instances
warehouse_schema = WarehouseSchema()
many_warehouse_schema = WarehouseSchema(many=True)
