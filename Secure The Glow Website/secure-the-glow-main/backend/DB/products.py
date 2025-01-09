from app import logger, db, text, Blueprint, datetime, argon2
from flask import abort, jsonify, request, make_response
import re
import magic
from werkzeug.utils import secure_filename
import os
import pyclamd
from model.product_images import ProductImages
from model.product import Product, product_schema, many_product_schema
from model.product_ingredients import ProductIngredients, product_ingredients_schema
import base64
import traceback

product_routes = Blueprint('product_routes', __name__)

CATEGORIES = {
  "sun care": ["sunscreen", "tanning oil", "after sun"],
  "eyes": ["mascara", "eyeshadow"],
  "cleansers": ["face wash", "micellar water", "cleansing balm"],
  "moisturizers": ["day cream", "night cream", "hydrating gel"],
  "anti-aging": ["retinol cream", "firming serum", "anti-wrinkle lotion"],
  "exfoliators": ["face scrub", "chemical exfoliant", "peel"],
  "lip care": ["lip balm", "lip mask", "lip scrub"],
  "masks": ["clay mask", "sheet mask", "overnight mask"],
  "toners": ["hydrating toner", "exfoliating toner", "pH balancing toner"],
  "serums": ["vitamin C serum", "hyaluronic acid", "niacinamide serum"]
}

@product_routes.route("/create_product", methods = ["POST"])
def create_product():
    email = request.json["email"]
    name = request.json["name"]
    color = request.json["color"]
    quantity = request.json["quantity"]
    description = request.json["description"]
    gold_price = request.json["gold_price"]
    premium_price = request.json["premium_price"]
    regular_price = request.json["regular_price"]
    category = request.json["category"]
    sub_category = request.json["sub_category"]
    pao = request.json["pao"]
    discount = request.json['discount']

    try:
        p = Product(name, color, quantity, description, gold_price, premium_price, regular_price, category, sub_category, pao, discount)
        db.session.add(p)
        db.session.commit()
        logger.info(f"product {name, color, quantity} added by {email}")
        return jsonify({"message": "successfully added"}), 201

    except Exception as e:
        logger.warning(f"Failed to add product {name, color, quantity} by {email}: {e}")
        abort(400)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = os.path.join('DB','product_images')

def allowed_file_type(file_path):
    # Use magic to determine the file type
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_file(file_path)
    print(f"Detected MIME type: {file_mime_type}")
    print(file_mime_type in ['image/png', 'image/jpeg', 'image/jpg'])
    return file_mime_type in ['image/png', 'image/jpeg', 'image/jpg']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def scan_file(file_path):
    try:
        cd = pyclamd.ClamdNetworkSocket()
        result = cd.scan_file(file_path)
        return result
    except Exception as e:
        logger.error(f"Error scanning file: {e}")
        logger.error("You might want to download and confugure and run clamAV first")
        return None

@product_routes.route("/add_image", methods = ["POST"])
def add_image():
    if 'file' not in request.files:
        logger.warning("No file to upload")
        abort(400)
    file = request.files.get('file')
    print(file)
    if file.filename == '':
        logger.warning('No selected file')
        abort(400)
    
    #Save the file if extention is allowed
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename) #removed ../ w hek 
        print("entered secure file name\n")
        print(filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            logger.error(f"{file_path} already exists. choose another name.")
            abort(409)
        try:
            file.save(file_path)  # Save the file
            prod_name = request.form.get("name")
            pic = ProductImages(prod_name, file_path)
            db.session.add(pic)
            db.session.commit()
            logger.info(f'File {filename} successfully saved in {file_path}')
        except Exception as e:
            logger.error(f'Error saving file: {filename}: {e}')
            abort(503)
        # Check the file type using magic
        if not allowed_file_type(file_path):
            os.remove(file_path)
            db.session.execute(text("delete from secureglow.product_images where image_url = :file_path"), {"file_path": file_path})
            db.session.commit()
            logger.warning(f'Filetype of {filename} not allowed')
            abort(400)
        
        # Scan the file with ClamAV
        full_path = os.path.abspath(file_path)
        scan_result = scan_file(full_path)
        if scan_result and any(scan_result.values()):
            os.remove(file_path)
            db.session.execute(text("delete from secureglow.product_images where image_url = :file_path"), {"file_path": file_path})
            db.session.commit()
            logger.warning(f'File {file_path} is infected and has been removed.')
            abort(422)

        else:
            logger.info(f'File {filename} uploaded and scanned successfully.')
            return jsonify({"message": "successfully uploaded image"}), 201
        
    else:
        logger.warning(f"invalid file extention: {file.filename}")
        abort(400)

@product_routes.route("/update_product/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    # Get the product by its ID
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Get fields from JSON and update only if they are provided
    data = request.json

    if "name" in data:
        name = data["name"]
        if not re.match(VALID_NAME_PATTERN, name):
            return jsonify({"error": "Invalid 'name'. It can only contain letters, spaces, underscores, or hyphens."}), 400
        product.name = name
    if "color" in data:
        color = data["color"]
        if not re.match(VALID_COLOR_PATTERN, color):
            return jsonify({"error": "Invalid 'color'. It can only contain letters, spaces, underscores, or hyphens."}), 400
        product.color = color
    if "quantity" in data:
        quantity = data["quantity"]
        if not re.match(VALID_QUANTITY_PATTERN, quantity):
            return jsonify({"error": "Invalid 'quantity'. ."}), 400
        
        product.quantity = quantity
    if "description" in data:
        description = data["description"]
        if not re.match(VALID_DESCRIPTION_PATTERN, description):
            return jsonify({"error": "Invalid 'description'. It can only contain letters, digits, spaces, commas, periods, hyphens, or underscores."}), 400

        product.description = description
    if "gold_price" in data:
        gold_price = data["gold_price"]
        try:
            int(gold_price)
        except:
            abort(400)
        product.gold_price = gold_price
    if "premium_price" in data:
        premium_price = data["premium_price"]
        try:
            int(premium_price)
        except:
            abort(400)
        product.premium_price = premium_price
    if "regular_price" in data:
        regular_price = data["regular_price"]
        try:
            int(regular_price)
        except:
            abort(400)
        product.regular_price = regular_price
    if "category" in data:
        category =  data["category"]
        if category not in CATEGORIES:
            abort(400)
        product.category = category
    if "sub_category" in data:
        sub_category = data["sub_category"]
        if sub_category not in CATEGORIES[category]:
            abort(400)
        product.sub_category = sub_category
    if "pao" in data:
        pao = data["pao"]
        if not re.match(VALID_PAO_PATTERN, pao):
            return jsonify({"error": "Invalid 'pao'. It can only contain letters and digits."}), 400
        product.pao = pao
    if "gold_visible" in data:
        gold_visible = data["gold_visible"]
        if gold_visible not in [0, 1]:
            abort(400)
        product.gold_visible = gold_visible
    if "premium_visible" in data:
        premium_visible = data["premium_visible"]
        if premium_visible not in [0, 1]:
            abort(400)
        product.premium_visible = premium_visible
    if "regular_visible" in data:
        regular_visible = data["regular_visible"]
        if regular_visible not in [0, 1]:
            abort(400)
        product.regular_visible = regular_visible
    if "discount" in data:
        discount = data["discount"]
        try:
            float(discount)
        except:
            abort(400)
        if float(discount) < 0 or float(discount) > 100:
            abort (400)
        product.discount = discount
    try:
        db.session.commit()
        logger.info(f"Product {product_id} updated by {data.get('email')}")
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.warning(f"Failed to update product {product_id} by {data.get('email')}: {e}")
        return jsonify({"error": "Failed to update product"}), 400

@product_routes.route("/delete_product/<int:product_id>", methods = ["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404

    try:
        db.session.delete(product)  
        db.session.commit()       
        logger.info(f"Product {product_id} deleted successfully")
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()  #!     
        logger.warning(f"Failed to delete product {product_id}: {e}")
        return jsonify({"error": "Failed to delete product"}), 500
    
@product_routes.route("/add_ingredient", methods=["POST"])
def add_ingredient():
    try:
        product = request.json["name"]
        ingredient = request.json["ingredient"]
        i = ProductIngredients(product, ingredient)
        db.session.add(i)
        db.session.commit()
        logger.info(f"ingredient {ingredient} added to {product}")
        return jsonify({"message": "Ingredient added successfully"}), 201
    except Exception as e:
        logger.error(f"Failed to add ingredient: {e}")
        abort(409)
    
@product_routes.route("/delete_ingredient", methods=["DELETE"])
def delete_ingredient():
    try:
        data = request.json
        product = data["name"]    
        ingredient = data["ingredient"] 

        ingredient_entry = ProductIngredients.query.filter_by(name=product, ingredient=ingredient).first()

        if not ingredient_entry:
            return jsonify({"error": "Ingredient not found"}), 404
        
        db.session.delete(ingredient_entry)
        db.session.commit()

        logger.info(f"Ingredient {ingredient} deleted from {product}")
        return jsonify({"message": "Ingredient deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Failed to delete ingredient: {e}")
        abort(503)

@product_routes.route("/delete_image", methods=["DELETE"])
def delete_image():
    try:
        data = request.json
        product = data["name"]    
        image_name = data["image_name"] 
        image_url = image_name

        image_entry = ProductImages.query.filter_by(name=product, image_url=image_url).first()
        
        if not image_entry:
            logger.info(f"image {image_url} not found for {product}")
            return jsonify({"error": "image not found"}), 404
        
        os.remove(image_url)
        db.session.delete(image_entry)
        db.session.commit()

        logger.info(f"image {image_url} deleted from {product}")
        return jsonify({"message": "image deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Failed to delete image: {e}")
        abort(503)

@product_routes.route("/all_products", methods=["GET"])
def get_all_products():    
    try:
        products = Product.query.all()
        product_list = []
        for product in products:
            
            image = ProductImages.query.filter_by(name=product.name).first()
            product_dict = product_schema.dump(product)
            
            if image:
                # Read the image file and encode it in Base64
                with open(image.image_url, "rb") as img_file:
                    encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
                    product_dict["image_base64"] = encoded_image  # Add Base64 image data to product
            
            product_list.append(product_dict)

        return jsonify(product_list), 200
    except Exception as e:
        logger.error(f'Failed to retrieve products: {e}')
        abort(500)

@product_routes.route("/get_product/<int:product_id>", methods = ["GET"])
def get_product_by_id(product_id):
    try:
        # Get the product by ID
        product = Product.query.get(product_id)
        if not product:
            abort(404, description="Product not found")

        # Convert product to dictionary format
        product_dict = product_schema.dump(product)

        # Get all images for the product
        images = ProductImages.query.filter_by(name=product.name).all()
        product_dict["images_base64"] = []

        for image in images:
            # Read each image file and encode in Base64
            with open(image.image_url, "rb") as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
                product_dict["images_base64"].append([image.image_url , encoded_image])  # Add to images list

        return jsonify(product_dict), 200
    except Exception as e:
        logger.error(f'Failed to retrieve product with ID {product_id}: {e}')
        abort(500)

@product_routes.route('/get_ingredients/<int:id>', methods = ["GET"])
def get_ingredients(id):
    name = db.session.execute(text("select name from secureglow.product where id = :id"), {"id": id}).fetchone()[0]
    ingredients = ProductIngredients.query.filter_by(name=name).all()
    logger.info(f"Ingredients retrieved for {name}")
    return jsonify(product_ingredients_schema.dump(ingredients)), 200

VALID_NAME_PATTERN = r'^[A-Za-z\s_-]+$'  # Letters, spaces, hyphens, and underscores
VALID_COLOR_PATTERN = r'^[A-Za-z\s_-]+$'  # Letters, spaces, hyphens, and underscores
VALID_DESCRIPTION_PATTERN = r'^[a-zA-Z0-9()_\-\s]+$' #letters, numbers, parenthesis, underscores, dashes, spaces
VALID_QUANTITY_PATTERN = r'^[A-Za-z0-9\s,._-]+$'
VALID_PAO_PATTERN = r'^[A-Za-z0-9]+$'  # Letters and digits only

def validate_input(name, color, quantity, description, gold_price, premium_price, regular_price, pao):
    
    # Validate each field using the regex patterns
    if not re.match(VALID_NAME_PATTERN, name[0]):
        return jsonify({"error": "Invalid 'name'. It can only contain letters, spaces, underscores, or hyphens."}), 400

    if not re.match(VALID_COLOR_PATTERN, color[0]):
        return jsonify({"error": "Invalid 'color'. It can only contain letters, spaces, underscores, or hyphens."}), 400
    
    if not re.match(VALID_QUANTITY_PATTERN, quantity[0]):
        return jsonify({"error": "Invalid 'quantity'. It must be a positive integer."}), 400

    if not re.match(VALID_DESCRIPTION_PATTERN, description[0]):
        return jsonify({"error": "Invalid 'description'. It can only contain letters, digits, spaces, commas, periods, hyphens, or underscores."}), 400

    try:
        gold_price = int(gold_price[0])
        premium_price = int(premium_price[0])
        regular_price = int(regular_price[0])
    except ValueError:
        return jsonify({"error": "Prices must be valid integers."}), 400
    
    if not re.match(VALID_PAO_PATTERN, pao[0]):
        return jsonify({"error": "Invalid 'pao'. It can only contain letters and digits."}), 400

    return None  # No validation errors
    
@product_routes.route("/upload_products_csv", methods=["POST"])
def upload_products_csv():
    email = request.json["email"]
    products = request.json["products"]

    try:
        new_products = []
        ingredient_entries = []
        for product_data in products:
            name=product_data["name"],
            color=product_data["color"],
            quantity=product_data["quantity"],
            description=product_data["description"],
            gold_price=float(product_data["gold_price"]),
            premium_price=float(product_data["premium_price"]),
            regular_price=float(product_data["regular_price"]),
            category=product_data["category"],
            sub_category=product_data["sub_category"],
            pao=product_data["pao"]
            discount = product_data["discount"]
            try:
                float(discount)
            except:
                abort(400)
            if float(discount) < 0 or float(discount) > 100:
                abort (400)

            validation_error = validate_input(name, color, quantity, description, gold_price, premium_price, regular_price, pao)
            if validation_error:
                return validation_error
            
            if category[0] not in CATEGORIES:
                logger.warning(f"User {email} attempted to add invalid category {category}")
                abort(400)
            if sub_category[0] not in CATEGORIES[category[0]]:
                logger.warning(f"User {email} attempted to add invalid subcategory {sub_category} within {category}")
                abort(400)
            
            p = Product(name, color, quantity, description, gold_price, premium_price, regular_price, category, sub_category, pao, discount)
            
            ingredients = product_data['ingredients'].split(',')
            for ing in ingredients:
                i = ProductIngredients(product_data["name"], ing)
                ingredient_entries.append(i)
            new_products.append(p)

        db.session.bulk_save_objects(new_products)
        db.session.bulk_save_objects(ingredient_entries)
        db.session.commit()
        logger.info(f"Products uploaded by {email}")
        return jsonify({"message": "Products added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        traceback.print_exc() 
        logger.warning(f"Failed to upload products by {email}: {e}")
        abort(400)