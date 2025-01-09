from flask import Blueprint, request, jsonify, abort
from model.warehouse import WarehouseProduct, Warehouse
from app import db
from sqlalchemy import func
import re
from app import logger

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

# Route to update stock level for a product in a warehouse
@inventory_routes.route('/update_stock_level', methods=['POST'])
def update_stock_level():
    try:
        data = request.get_json()
        warehouse_id = data.get("warehouse_id")
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        validate_id(warehouse_id)
        validate_id(product_id)
        validate_quantity(quantity)

        warehouse_product = WarehouseProduct.query.filter_by(
            warehouse_id=warehouse_id, product_id=product_id
        ).first()

        if warehouse_product:
            warehouse_product.quantity += quantity
            db.session.commit()
            return jsonify({
                "success": True,
                "quantity": warehouse_product.quantity,
                "low_stock_alert": warehouse_product.quantity < 10
            }), 200

        return jsonify({"success": False, "message": "Product not found in warehouse"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error updating stock: {str(e)}"}), 500


# Route to fetch all warehouses with products
@inventory_routes.route('/warehouses', methods=['GET'])
def get_all_warehouses():
    try:
        warehouses = Warehouse.query.all()
        return jsonify([
            {
                "warehouse_id": warehouse.warehouse_id,
                "warehouse_name": warehouse.warehouse_name,
                "location": warehouse.location
            } for warehouse in warehouses
        ]), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error fetching warehouses: {str(e)}"}), 500


# Route to fetch a specific warehouse by ID
@inventory_routes.route('/warehouse/<int:warehouse_id>', methods=['GET'])
def get_warehouse_by_id(warehouse_id):
    if not isinstance(warehouse_id, int):
        abort(400)
    try:
        warehouse = Warehouse.query.get(warehouse_id)
        if warehouse:
            return jsonify({
                "warehouse_id": warehouse.warehouse_id,
                "warehouse_name": warehouse.warehouse_name,
                "location": warehouse.location,
                "products": [
                    {
                        "product_id": wp.product_id,
                        "quantity": wp.quantity
                    } for wp in warehouse.products
                ]
            }), 200
        return jsonify({"error": "Warehouse not found"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error fetching warehouse: {str(e)}"}), 500


# Route to generate inventory report
@inventory_routes.route('/inventory_report', methods=['GET'])
def generate_inventory_report():
    try:
        # Historical turnover data (mock logic for turnover rate)
        turnover_data = db.session.query(
            WarehouseProduct.product_id,
            func.sum(WarehouseProduct.quantity).label("current_stock"),
            func.count(WarehouseProduct.warehouse_id).label("warehouse_count"),
            func.sum(WarehouseProduct.quantity) / func.count(WarehouseProduct.warehouse_id).label("avg_turnover_rate")
        ).group_by(WarehouseProduct.product_id).all()

        # Predict turnover based on mock average turnover rates
        turnover_report = [
            {
                "product_id": t[0],
                "current_stock": float(t[1]),
                "warehouse_count": t[2],
                "predicted_turnover": round(float(t[1]) / max(float(t[3]), 1), 2)  #Stock divided by average turnover rate
            }
            for t in turnover_data
        ]

        # Most popular products report (based on sales or stock movement trends)
        popular_products_data = db.session.query(
            WarehouseProduct.product_id,
            func.sum(WarehouseProduct.quantity).label("total_stock"),
            func.count(WarehouseProduct.warehouse_id).label("warehouse_count"),
            (func.sum(WarehouseProduct.quantity) * 1.1).label("predicted_popularity_index")  # Mock popularity index
        ).group_by(WarehouseProduct.product_id).order_by(func.sum(WarehouseProduct.quantity).desc()).limit(5).all()

        # Popular products report
        popular_products_report = [
            {
                "product_id": p[0],
                "current_stock": float(p[1]),
                "warehouse_count": p[2],
                "predicted_popularity_index": round(float(p[3]), 2)  # Popularity trend
            }
            for p in popular_products_data
        ]

        # Demand predictions (based on historical depletion and restocking trends)
        demand_predictions = [
            {
                "product_id": t[0],
                "predicted_demand": round(float(t[1]) * 1.2, 2),  #Increase demand by 20%
                "current_stock": float(t[1]),
                "warehouse_count": t[2],
                "turnover_rate": round(float(t[3]), 2)  # Use historical turnover rate for better predictions
            }
            for t in turnover_data
        ]

        # Final report structure
        report = {
            "turnover_report": turnover_report,
            "popular_products": popular_products_report,
            "demand_predictions": demand_predictions
        }

        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Error generating inventory report: {e}")
        return jsonify({"error": f"Error generating inventory report: {str(e)}"}), 500
