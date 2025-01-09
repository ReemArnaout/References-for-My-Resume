import sys
sys.path.append("..") 
from app import ma, db

class ProductImages(db.Model):
    name = db.Column(db.String(50), db.ForeignKey('product.name', ondelete='CASCADE'), primary_key = True)
    image_url = db.Column(db.String(128), primary_key = True)

    def __init__(self, name, image_url):
        super(ProductImages, self).__init__(name = name, image_url = image_url)
        
    
class ProductImagesSchema(ma.Schema):
    class Meta:
        fields = ("name", "image_url")
        model = ProductImages

product_images_schema = ProductImagesSchema(many = True)