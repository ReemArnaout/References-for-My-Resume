import sys
sys.path.append("..") 
from app import ma, db

class ProductInstance(db.Model):
    name = db.Column(db.String(50), db.ForeignKey('product.name', ondelete='CASCADE'), primary_key = True)
    color = db.Column(db.String(20), primary_key = True)
    quantity = db.Column(db.String(10), primary_key = True)
    serial_number = db.Column(db.String(30), primary_key = True)
    bought = db.Column(db.Boolean)
    def __init__(self, name, color, quantity, serial_number):
        super(ProductInstance, self).__init__(name = name, color = color, quantity = quantity, serial_number = serial_number)
        self.bought = False
class ProductInstanceSchema(ma.Schema):
    class Meta:
        fields = ("name", "color", "quantity", "serial_number", "bought")
        model = ProductInstance

product_instance_schema = ProductInstanceSchema(many=True)