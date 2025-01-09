from app import logger, csrf
from flask import Blueprint, request, jsonify, abort
from authentication import token_required
import re
import requests

inventory_routes = Blueprint('inventory_routes', __name__)

# Validation Patterns
VALID_ID_PATTERN = r'^\d+$'
VALID_QUANTITY_PATTERN = r'^\d+$'

def validate_id(value):
    if not re.match(VALID_ID_PATTERN, str(value)):
        logger.warning(f"Invalid ID format: {value}")
        abort(400, description="Invalid ID format.")

def validate_quantity(value):
    if not re.match(VALID_QUANTITY_PATTERN, str(value)):
        logger.warning(f"Invalid quantity format: {value}")
        abort(400, description="Invalid quantity format.")


# Route to update the stock level for a product in a warehouse
@inventory_routes.route('/update_stock_level', methods=['POST'])
@token_required
def update_stock_level(email, roles):
    logger.info(f"User {email} roles: {roles}")
    if "stocking-employee" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to update stock level")
        abort(403)

    data = request.get_json()
    warehouse_id = data.get("warehouse_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    validate_id(warehouse_id)
    validate_id(product_id)
    validate_quantity(quantity)

    payload = {
        "warehouse_id": warehouse_id,
        "product_id": product_id,
        "quantity": quantity
    }

    try:
        url = "http://localhost:5001/update_stock_level"
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logger.error(f"Error updating stock level: {e}")
        abort(500, description="Error updating stock level")

# Route to fetch all warehouses with products
@inventory_routes.route('/warehouses', methods=['GET'])
@token_required
@csrf.exempt
def get_all_warehouses(email, roles):
    logger.info(f"User {email} roles: {roles}")
    if "stocking-employee" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to fetch warehouses")
        abort(403)

    try:
        url = "http://localhost:5001/warehouses"
        response = requests.get(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logger.error(f"Error fetching warehouses: {e}")
        abort(500, description="Error fetching warehouses")

# Route to fetch a specific warehouse by ID
@inventory_routes.route('/warehouse/<int:warehouse_id>', methods=['GET'])
@token_required
@csrf.exempt
def get_warehouse_by_id(email, roles, warehouse_id):
    logger.info(f"User {email} roles: {roles}")
    if "stocking-employee" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to fetch warehouse {warehouse_id}")
        abort(403)
    if not isinstance(warehouse_id, int):
        abort(400)

    try:
        url = f"http://localhost:5001/warehouse/{warehouse_id}"
        response = requests.get(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logger.error(f"Error fetching warehouse by ID: {e}")
        abort(500, description="Error fetching warehouse by ID")

# Route to generate inventory report
@inventory_routes.route('/inventory_report', methods=['GET'])
@token_required
@csrf.exempt
def generate_report(email, roles):
    logger.info(f"User {email} roles: {roles}")
    if "marketing-analyst" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to generate inventory report")
        abort(403)

    try:
        url = "http://localhost:5001/inventory_report"
        response = requests.get(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logger.error(f"Error generating inventory report: {e}")
        abort(500, description="Error generating inventory report")