from app import logger, csrf
from flask import abort, jsonify, request, Blueprint, make_response, current_app
from authentication import token_required
import requests
import csv
import magic
from werkzeug.utils import secure_filename
import re

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

VALID_NAME_PATTERN = r'^[A-Za-z\s_-]+$'  # Letters, spaces, hyphens, and underscores
VALID_COLOR_PATTERN = r'^[A-Za-z\s_-]+$'  # Letters, spaces, hyphens, and underscores
VALID_DESCRIPTION_PATTERN = r'^[a-zA-Z0-9()_\-\s]+$' #letters, numbers, parenthesis, underscores, dashes, spaces
VALID_QUANTITY_PATTERN = r'^[A-Za-z0-9\s,._-]+$'
VALID_PAO_PATTERN = r'^[A-Za-z0-9]+$'  # Letters and digits only

def validate_input(name, color, quantity, description, gold_price, premium_price, regular_price, pao):
        
    # Validate each field using the regex patterns
    if not re.match(VALID_NAME_PATTERN, name):
        return jsonify({"error": "Invalid 'name'. It can only contain letters, spaces, underscores, or hyphens."}), 400

    if not re.match(VALID_COLOR_PATTERN, color):
        return jsonify({"error": "Invalid 'color'. It can only contain letters, spaces, underscores, or hyphens."}), 400
    
    if not re.match(VALID_QUANTITY_PATTERN, quantity):
        return jsonify({"error": "Invalid 'quantity'. ."}), 400

    if not re.match(VALID_DESCRIPTION_PATTERN, description):
        return jsonify({"error": "Invalid 'description'. It can only contain letters, digits, spaces, commas, periods, hyphens, or underscores."}), 400

    try:
        gold_price = int(gold_price)
        premium_price = int(premium_price)
        regular_price = int(regular_price)
    except ValueError:
        return jsonify({"error": "Prices must be valid integers."}), 400

    # Validate PAO (string of chars/digits)
    if not re.match(VALID_PAO_PATTERN, pao):
        return jsonify({"error": "Invalid 'pao'. It can only contain letters and digits."}), 400

    return None  # No validation errors

@product_routes.route('/create_product', methods = ['POST'])
@token_required
def create_product(email, roles):
    if "business-manager" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product")
        abort(403)
    
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
    discount = request.json["discount"]

    try:
        float(discount)
    except:
        abort(400)
    if float(discount) < 0 or float(discount) > 100:
        abort (400)

    validation_error = validate_input(name, color, quantity, description, gold_price, premium_price, regular_price, pao)
    if validation_error:
        return validation_error

    if category not in CATEGORIES:
        logger.warning(f"User {email} attempted to add invalid category {category}")
        abort(400)
    if sub_category not in CATEGORIES[category]:
        logger.warning(f"User {email} attempted to add invalid subcategory {sub_category} within {category}")
        abort(400)
    if not (name and color and quantity):
        logger.warning(f"User {email} attempted to leave empty values in mandatory fields")
        abort(400)

    url = "http://localhost:5001/create_product" 
    data = {
        "name": name,
        "color": color,
        "quantity": quantity,
        "description": description,
        "gold_price": gold_price,
        "premium_price": premium_price,
        "regular_price": regular_price,
        "category": category,
        "sub_category": sub_category,
        "pao": pao,
        "email": email,
        "discount":discount
    }
    response = requests.post(url, json=data)
    if response.status_code == 400:
        logger.warning(f"Failed to add product {name, color, quantity} by {email}")
        abort(400)
    return jsonify({"message": "successfully added"}), 201

@product_routes.route("/upload_image", methods=["POST"])
@token_required
def upload_image(email, roles):
    if "business-manager" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product image")
        abort(403)
    try:
        image = request.files.get('file')
        prod_name = request.form.get("name")
        url = "http://localhost:5001/add_image" 
        data = {"name": prod_name}
        files = {'file': (image.filename, image, image.content_type)}
        print(image)
        response = requests.post(url, data=data, files=files)
        if response.status_code ==  201:
            logger.info(f"uploaded {prod_name} photo {image.filename}")
            return jsonify({"message": "upload successful"}), 201
        logger.warning(f"failed to upload by {email}")
        abort(response.status_code)
    except Exception as e:
        logger.error(f"failed to upload by {email}: {e}")
        abort(400)

@product_routes.route("/edit_product/<int:product_id>", methods=["PUT"])
@token_required
def edit_product(email, roles, product_id):
    if "business-manager" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product image")
        abort(403)
    if not isinstance(product_id, int):
        abort(400)
    url = "http://localhost:5001/update_product/" + str(product_id)
    data = request.json
    data["email"] = email
    try:
        response = requests.put(url, json=data)
        if response.status_code != 200:
            abort(400)
        return({"message": "successfully updated"}), 200
    except Exception as e:
        logger.error(f'Failed to edit product with id {product_id}: {e}')
        abort(404)

@product_routes.route("/delete_product/<int:product_id>", methods = ["DELETE"])
@token_required
def delete_product(email, roles, product_id):
    if "business-manager" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product image")
        abort(403)
    if not isinstance(product_id, int):
        abort(400)
    url = "http://localhost:5001/delete_product/" + str(product_id)
    try:
        response = requests.delete(url)
        if response.status_code != 200:
            logger.info(f"product {product_id} couldnt be deleted by {email}")
            abort(404)
        logger.info(f"product {product_id} deleted by {email}")
        return({"message": "successfully deleted"}), 200
    except Exception as e:
        logger.error(f'Failed to delete product with id {product_id}: {e}')
        abort(404)

VALID_INGREDIENT_PATTERN = r'^[A-Za-z0-9\s,._&-]+$'  # Letters, digits, spaces, commas, periods, &, -, _
VALID_NAME_PATTERN = r'^[A-Za-z\s_-]+$'  # Letters, spaces, hyphens, and underscores

@product_routes.route("/add_ingredient", methods = ["POST"])
@token_required
def add_ingredient(email, roles):
    if "business-manager" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product ingredient")
        abort(403)
    try:
        if not re.match(VALID_INGREDIENT_PATTERN, request.json['ingredient']):
            return jsonify({"error": "Invalid 'ingredient'. It can only contain letters, digits, spaces, commas, periods, &, -, or _."}), 400

        if not re.match(VALID_NAME_PATTERN, request.json['name']):
            return jsonify({"error": "Invalid 'name'. It can only contain letters, spaces, hyphens, or underscores."}), 400
    
        url = "http://localhost:5001/add_ingredient"
        response = requests.post(url = url, json = request.json)
        if response.status_code == 201:
            logger.info(f"ingredient {request.json['ingredient']} added to {request.json['name']}")
            return jsonify({"message": "Ingredient added successfully"}), 201
        abort(409)
    except Exception as e:
        logger.error(f"Failed to add ingredient: {e}")
        abort(409)

@product_routes.route("/delete_ingredient", methods = ["DELETE"])
@token_required
def delete_ingredient(email, roles):
    if "business-manager" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product image")
        abort(403)
    try:
        url = "http://localhost:5001/delete_ingredient"
        response = requests.delete(url = url, json = request.json)
        if response.status_code == 200:
            logger.info(f"ingredient {request.json['ingredient']} deleted from {request.json['name']}")
            return jsonify({"message": "Ingredient deleted successfully"}), 200
        abort(404)
    except Exception as e:
        logger.error("Failed to add ingredient")
        abort(503)

@product_routes.route("/delete_image", methods = ["DELETE"])
@token_required
def delete_image(email, roles):
    if "business-manager" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product image")
        abort(403)
    try:
        url = "http://localhost:5001/delete_image"
        response = requests.delete(url = url, json = request.json)
        if response.status_code == 200:
            logger.info(f"image {request.json['image_name']} deleted from {request.json['name']}")
            return jsonify({"message": "image deleted successfully"}), 200
        abort(404)
    except Exception as e:
        logger.error(f"failed to delete image: {e}")
        abort(404)

@product_routes.route("/all_products", methods=["GET"])
@token_required
@csrf.exempt
def get_all_products(email, roles):
    if "business-manager" not in roles and "stocking-employee" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product image")
        abort(403)
    try:
        url = "http://localhost:5001/all_products"
        response = requests.get(url = url)
        return jsonify(response.json()), 200
    except Exception as e:
        logger.error(f'Failed to retrieve products: {e}')
        abort(500)

@product_routes.route("/get_product/<int:product_id>", methods=["GET"])
@token_required
@csrf.exempt
def get_product(email, roles, product_id):
    if "business-manager" not in roles and "stocking-employee" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product image")
        abort(403)
    if not isinstance(product_id, int):
        abort(400)
    try:
        url = "http://localhost:5001/get_product/"+str(product_id)
        response = requests.get(url = url)
        return jsonify(response.json()), 200
    except Exception as e:
        logger.error(f'Failed to retrieve products: {e}')
        abort(500)

@product_routes.route('/get_ingredients/<int:id>', methods = ["GET"])
@token_required
@csrf.exempt
def get_ingredients(email, roles, id ):
    if "business-manager" not in roles and "stocking-employee" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to add a new product image")
        abort(403)
    if not isinstance(id, int):
        abort(400)
    try:
        url = "http://localhost:5001/get_ingredients/"+str(id)
        data = {'id': id}
        response = requests.get(url = url, json = data)
        return jsonify(response.json()), 200
    except Exception as e:
        logger.error(e)
        abort(500)

@product_routes.route('/upload_products_csv', methods=['POST'])
@token_required
def upload_products_csv(email, roles):
    if "business-manager" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to upload products via CSV")
        abort(403)

    if 'file' not in request.files:
        logger.warning(f"No file part in the request by {email}")
        abort(400)

    file = request.files['file']
    filename = secure_filename(file.filename)
    if filename == '' or not file:
        logger.warning(f"No selected file by {email}")
        abort(400)

    if ('.' in file and filename.rsplit('.', 1)[1].lower() != ['csv']):
        logger.warning(f"Invalid file type uploaded by {email}")
        abort(400)

    file.seek(0)
    csv_data = file.read().decode('utf-8')
    products = []
    reader = csv.DictReader(csv_data.splitlines())
    for row in reader:
        products.append(row)
    
    # Send the list of products to the database service
    url = "http://localhost:5001/upload_products_csv"
    response = requests.post(url, json={"products": products, "email": email})
    if response.status_code != 201:
        logger.warning(f"Failed to upload products via CSV by {email}")
        abort(400)

    return jsonify({"message": "CSV uploaded successfully"}), 201

        
