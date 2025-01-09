from app import logger
from flask import abort, jsonify, request, Blueprint
from authentication import token_required
import requests

order_routes = Blueprint('order_routes', __name__)
@order_routes.route('/create_order', methods=['POST'])
@token_required
def create_order(email, roles):
    logger.info(f"User {email} roles: {roles}")
    if "customer-service-specialist" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to create a new order")
        abort(403)

    # Extracting the order details from request data
    customer_email = request.json.get("customer_email")
    delivery_time_slot = request.json.get("delivery_time_slot")
    payment_method = request.json.get("payment_method")
    products = request.json.get("products")  # Now expecting a list of products
    instore_pickup = request.json.get("instore_pickup", "").strip()  # Default to an empty string if not provided
    delivery_address = request.json.get("delivery_address","").strip()

    # Basic validation
    if not (customer_email and delivery_time_slot and payment_method and products):
        logger.warning(f"User {email} attempted to leave empty values in mandatory fields")
        abort(400)

    # Additional validation for delivery address if instore_pickup is blank
    if not instore_pickup and not delivery_address:
        logger.warning(f"User {email} did not provide a delivery address for non-pickup order")
        abort(400)
    # Validate product entries
    for product in products:
        print(product)
        if not ("product_id" in product and "quantity" in product):
            logger.warning(f"User {email} provided incomplete product details")
            abort(400)
    
    # Payload for the API request to create the order
    url = "http://localhost:5001/create_order"
    data = {
        "customer_email": customer_email,
        "delivery_time_slot": delivery_time_slot,
        "payment_method": payment_method,
        "products": products,  # Pass the list of products directly
        "instore_pickup": instore_pickup or None,  # Pass store name or None
        "delivery_address": delivery_address if not instore_pickup else None  # Only include if instore_pickup is blank
    }
    print(data)
    try:
        response = requests.post(url, json=data)
        if response.status_code != 201:
            logger.warning(f"Failed to create order for customer {customer_email} by {email}")
            abort(400)
        return jsonify({"message": "Order successfully created"}), 201
    except Exception as e:
        logger.error(f"Failed to create order: {e}")
        return jsonify({"message": "Failed to create order"}), 500

@order_routes.route("/orders", methods=["GET"])
@token_required
def get_orders(email, roles):
    logger.info(f"User {email} is requesting all orders.")

    # Check if the user has the appropriate role
    if "customer-service-specialist" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to access all orders")
        abort(403)

    # Define the URL to fetch orders from the DB service
    url = "http://localhost:5001/orders"
    try:
        # Send a GET request to the DB service
        response = requests.get(url)

        # Handle the response from the DB service
        if response.status_code != 200:
            logger.error("Failed to fetch orders from the DB service.")
            return jsonify({"error": "Failed to fetch orders"}), response.status_code

        # Return the JSON response from the DB service
        return jsonify(response.json()), 200

    except Exception as e:
        logger.error(f"Error while retrieving orders: {e}")
        return jsonify({"error": "Error retrieving orders"}), 500


@order_routes.route("/edit_order/<int:order_id>", methods=["PUT"])
@token_required
def edit_order(email, roles, order_id):
    if "customer-service-specialist" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to edit order {order_id}")
        abort(403)

    url = f"http://localhost:5001/edit_order/{order_id}"
    data = request.json
    data["email"] = email
    try:
        response = requests.put(url, json=data)
        if response.status_code != 200:
            abort(400)
        return jsonify({"message": "Order successfully updated"}), 200
    except Exception as e:
        logger.error(f'Failed to edit order with id {order_id}: {e}')
        abort(404)

@order_routes.route("/delete_order/<int:order_id>", methods=["DELETE"])
@token_required
def delete_order(email, roles, order_id):
    if "customer-service-specialist" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to delete order {order_id}")
        abort(403)

    url = f"http://localhost:5001/delete_order/{order_id}"
    try:
        response = requests.delete(url)
        if response.status_code != 200:
            logger.info(f"Order {order_id} could not be deleted by {email}")
            abort(404)
        logger.info(f"Order {order_id} deleted by {email}")
        return jsonify({"message": "Order successfully deleted"}), 200
    except Exception as e:
        logger.error(f'Failed to delete order with id {order_id}: {e}')
        return jsonify({"message": "Failed to delete."}), 404


    
@order_routes.route("/invoices", methods=["GET"])
@token_required
def admin_get_invoices(email, roles):
    if "customer-service-specialist" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to retrieve invoices")
        abort(403)

    url = "http://localhost:5001/invoices"  # URL to fetch from DB service
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logger.error("Failed to fetch invoices from DB.")
            return jsonify({"error": "Failed to fetch invoices"}), response.status_code

        # Return the JSON response from the DB service
        return jsonify(response.json()), 200

    except Exception as e:
        logger.error(f"Failed to retrieve invoices: {e}")
        return jsonify({"error": "Failed to retrieve invoices"}), 500
    

@order_routes.route("/get_invoice/<int:invoice_id>", methods=["GET"])
@token_required
def get_invoice(email, roles, invoice_id):
    logger.info(f"User {email} is requesting invoice {invoice_id}.")
    
    # Check if the user has the appropriate role
    if "customer-service-specialist" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to access invoice {invoice_id}")
        abort(403)

    url = f"http://localhost:5001/get_invoice/{invoice_id}"  # URL to fetch from DB service
    try:
        response = requests.get(url)
        
        if response.status_code == 404:
            logger.warning(f"Invoice {invoice_id} not found.")
            return jsonify({"error": "Invoice not found"}), 404
        elif response.status_code != 200:
            logger.error(f"Failed to fetch invoice {invoice_id} from DB.")
            return jsonify({"error": "Failed to fetch invoice"}), 500

        # Return the JSON response from the DB service
        return jsonify(response.json()), 200

    except Exception as e:
        logger.error(f"Error while retrieving invoice {invoice_id}: {e}")
        return jsonify({"error": "Error retrieving invoice"}), 500

@order_routes.route("/update_invoice_payment/<int:invoice_id>", methods=["PUT"])
@token_required
def update_invoice_payment(email, roles, invoice_id):
    logger.info(f"User {email} is attempting to update payment status for invoice {invoice_id}.")
    
    # Check if the user has the appropriate role
    if "customer-service-specialist" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to update payment status for invoice {invoice_id}")
        abort(403)

    # Get the payment status from the request payload
    data = request.get_json()
    if not data or "payment_status" not in data:
        logger.warning("Payment status not provided in request.")
        return jsonify({"error": "Payment status is required"}), 400

    # Forward the request to the DB service
    url = f"http://localhost:5001/update_invoice_payment/{invoice_id}"  # DB service endpoint
    try:
        response = requests.put(url, json=data)

        # Handle the response from the DB service
        if response.status_code == 404:
            logger.warning(f"Invoice {invoice_id} not found.")
            return jsonify({"error": "Invoice not found"}), 404
        elif response.status_code == 400:
            logger.warning(f"Invalid data for updating invoice {invoice_id}: {response.json()}")
            return jsonify(response.json()), 400
        elif response.status_code != 200:
            logger.error(f"Failed to update payment status for invoice {invoice_id}.")
            return jsonify({"error": "Failed to update payment status"}), 500

        # Return the successful response from the DB service
        return jsonify(response.json()), 200

    except Exception as e:
        logger.error(f"Error while updating payment status for invoice {invoice_id}: {e}")
        return jsonify({"error": "Error updating payment status"}), 500
    
    
@order_routes.route("/returns", methods=["GET"])
@token_required
def get_returns(email, roles):
    if "customer-service-specialist" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to fetch return requests")
        abort(403)

    logger.info(f"User {email} with roles {roles} is fetching return requests")
    
    url = "http://localhost:5001/returns"  # Forwarding the request to DB service
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"User {email} failed to fetch return requests from DB service")
            return jsonify({"error": "Failed to fetch return requests"}), response.status_code

        logger.info(f"User {email} successfully fetched return requests")
        return jsonify(response.json()), 200

    except Exception as e:
        logger.error(f"User {email} encountered an error while retrieving return requests: {e}")
        return jsonify({"error": "Failed to retrieve return requests"}), 500


@order_routes.route("/update_return_status/<int:return_id>", methods=["PUT"])
@token_required
def update_return_status(email, roles, return_id):
    if "customer-service-specialist" not in roles:
        logger.warning(f"Unauthorized attempt by {email} to update return request {return_id}")
        abort(403)

    data = request.get_json()
    if not data or "status" not in data:
        logger.warning(f"User {email} failed to provide return status in request")
        return jsonify({"error": "Return status is required"}), 400

    status = data["status"].lower()
    if status not in ["approved", "denied"]:
        logger.warning(f"User {email} provided an invalid return status: {status}")
        return jsonify({"error": "Invalid status. Valid statuses are 'approved' and 'denied'"}), 400

    url = f"http://localhost:5001/update_return_status/{return_id}"  # Forwarding to DB service
    try:
        response = requests.put(url, json=data)
        if response.status_code != 200:
            logger.error(f"User {email} failed to update return request {return_id}")
            return jsonify({"error": "Failed to update return request"}), response.status_code

        logger.info(f"User {email} successfully updated return request {return_id} to status '{status}'")
        return jsonify({"message": "Return status updated successfully"}), 200

    except Exception as e:
        logger.error(f"User {email} encountered an error while updating return status for request {return_id}: {e}")
        return jsonify({"error": "Failed to update return status"}), 500
