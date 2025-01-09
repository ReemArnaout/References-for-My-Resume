import sys
sys.path.append("..") 
from app import ma, db

class ProductIngredients(db.Model):
    name = db.Column(db.String(50), db.ForeignKey('product.name', ondelete='CASCADE'), primary_key = True)
    ingredient = db.Column(db.String(128), primary_key = True)

    def __init__(self, name, ingredient):
        super(ProductIngredients, self).__init__(name = name, ingredient = ingredient)
        
    
class ProductIngredientsSchema(ma.Schema):
    class Meta:
        fields = ("name", "ingredient")
        model = ProductIngredients

product_ingredients_schema = ProductIngredientsSchema(many = True)