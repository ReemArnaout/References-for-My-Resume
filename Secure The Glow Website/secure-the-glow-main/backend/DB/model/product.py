import sys
sys.path.append("..") 
from app import ma, db
from sqlalchemy import UniqueConstraint

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(50))
    color = db.Column(db.String(20))
    quantity = db.Column(db.String(10))
    description = db.Column(db.Text)
    gold_price = db.Column(db.Float)
    premium_price = db.Column(db.Float)
    regular_price = db.Column(db.Float)
    category = db.Column(db.String(30))
    sub_category = db.Column(db.String(30))
    pao = db.Column(db.String(10))
    gold_visible = db.Column(db.Boolean)
    premium_visible = db.Column(db.Boolean)
    regular_visible = db.Column(db.Boolean)
    discount = db.Column(db.Float)
    __table_args__ = (
        UniqueConstraint('name', 'quantity', 'color', name='uix_name_quantity'),
    )
    def __init__(self, name, color, quantity, description, gold_price, premium_price, regular_price, category, sub_category, pao, discount):
        super(Product, self).__init__(name = name, color = color, quantity = quantity, description = description, gold_price = gold_price, premium_price = premium_price, regular_price = regular_price, category = category, sub_category = sub_category, pao = pao, discount = discount)
        self.gold_visible = False
        self.premium_visible = False
        self.regular_visible = False
    
        
class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "color", "quantity", "description", "gold_price", "premium_price", "regular_price", "category", "sub_category", "pao", "gold_visible", "premium_visible", "regular_visible", "discount")
        model = Product

many_product_schema = ProductSchema(many=True)
product_schema = ProductSchema()