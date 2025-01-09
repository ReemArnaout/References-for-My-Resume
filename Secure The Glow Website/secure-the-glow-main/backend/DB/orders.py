# routes/orders.py

import re
from flask import Blueprint, jsonify, request, abort
from app import logger, db
from model.orders import Order, OrderProduct
from model.product import Product
from model.product_instance import ProductInstance
from model.user import User
from model.warehouse import WarehouseProduct, Warehouse
from model.invoice import Invoice, invoice_schema, invoices_schema, InvoiceProduct
from model.returns import Return
from model.credit_card_info import CreditCardInfo
import datetime

order_routes = Blueprint('order_routes', __name__)
@order_routes.route("/create_order", methods=["POST"])
def create_order():
    try:
        customer_email = request.json["customer_email"]
        delivery_time_slot = request.json["delivery_time_slot"]
        payment_method = request.json["payment_method"]
        products = request.json.get("products")  # List of products with product_id and quantity

        # Retrieve address information from request data
        delivery_address = request.json.get("delivery_address")
        instore_pickup = request.json.get("instore_pickup")

        # Ensure that either delivery_address or instore_pickup is provided
        if not delivery_address and not instore_pickup:
            logger.error("Either 'delivery_address' or 'instore_pickup' must be provided.")
            return jsonify({"error": "Either 'delivery_address' or 'instore_pickup' must be provided."}), 400

        
        # Validate delivery_address if provided
        if delivery_address:
            # Validate address format: City-Street-Building-Floor (floor must be numeric)
            address_pattern = r"^[a-zA-Z\s]+-[a-zA-Z\s]+-[a-zA-Z0-9\s]+-[0-9\s]+$"
            if not re.match(address_pattern, delivery_address):
                logger.error("Delivery address format is invalid. Expected format: City-Street-Building-Floor.")
                return jsonify({"error": "Delivery address format is invalid. Expected format: City-Street-Building-Floor."}), 400

        # Determine final address
        final_address = instore_pickup if instore_pickup else delivery_address
        # Check payment method and verify credit card information
        if payment_method.lower() == "credit card":
            credit_card_info = CreditCardInfo.query.filter_by(user_email=customer_email).first()
            if not credit_card_info:
                logger.error(f"No credit card information found for user {customer_email}")
                return jsonify({"error": "No credit card information found. Please add your credit card details."}), 400

        # Check that products list is provided and non-empty
        if not products or not isinstance(products, list):
            logger.error("Products list is required and should contain at least one product.")
            return jsonify({"error": "Products list is required and should contain at least one product"}), 400
        user = User.query.get(customer_email)
        if not user:
            logger.error("User not found")
            return jsonify({"error": "User not found"}), 404
        # Validate product quantities
        for product_entry in products:
            quantity_required = int(product_entry.get("quantity"))
            if quantity_required <= 0:
                logger.error(f"Quantity for product ID {product_entry.get('product_id')} must be positive.")
                return jsonify({"error": f"Quantity for product ID {product_entry.get('product_id')} must be positive."}), 400

        # Create the order
        order = Order(
            customer_email=customer_email,
            delivery_time_slot=delivery_time_slot,
            payment_method=payment_method,
            delivery_address=final_address
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID before committing

        # Check stock and create OrderProducts
        sufficient_stock = True
        for product_entry in products:
            product_id = product_entry.get("product_id")
            quantity_required = int(product_entry.get("quantity"))

            # Validate product existence
            product = Product.query.get(product_id)
            if not product:
                logger.error(f"Product with ID {product_id} not found.")
                return jsonify({"error": f"Product with ID {product_id} not found"}), 404

            # Check and allocate stock
            warehouses_with_product = WarehouseProduct.query.filter_by(product_id=product_id).all()
            quantity_to_allocate = quantity_required
            for warehouse_product in warehouses_with_product:
                if warehouse_product.quantity >= quantity_to_allocate:
                    warehouse_product.quantity -= quantity_to_allocate
                    quantity_to_allocate = 0
                    break
                else:
                    quantity_to_allocate -= warehouse_product.quantity
                    warehouse_product.quantity = 0

            if quantity_to_allocate > 0:
                sufficient_stock = False
                break

            # Add to OrderProduct
            order_item = OrderProduct(order_id=order.id, product_id=product_id, quantity=quantity_required)
            db.session.add(order_item)

        if not sufficient_stock:
            db.session.rollback()
            logger.error("Insufficient stock for one or more products")
            return jsonify({"error": "Insufficient stock for one or more products"}), 400

        # Update order status to 'processing'
        order.status = 'processing'

 


        # Determine user price tier
        price_tier_map = {"gold": "gold_price", "premium": "premium_price", "basic": "regular_price"}
        user_tier = user.tier.lower() if user and user.tier else "regular"
        price_field = price_tier_map.get(user_tier, "regular_price")

        # Calculate total amount and create invoice
        total_amount = 0
        invoice_products = []

        for order_product in order.products:
            product = Product.query.get(order_product.product_id)
            if product:
                product_price = getattr(product, price_field, 0) or 0
                if product.discount:
                    product_price -= product_price * (product.discount / 100)
                total_price = product_price * order_product.quantity
                total_amount += total_price

                invoice_product = InvoiceProduct(
                    product_id=product.id,
                    quantity=order_product.quantity,
                    price_at_time_of_purchase=product_price,
                    total_price=total_price
                )
                invoice_products.append(invoice_product)

        if total_amount <= 0:
            db.session.rollback()
            logger.error("Total amount is invalid")
            return jsonify({"error": "Total amount is invalid"}), 400

        invoice = Invoice(
            order_id=order.id,
            total_amount=total_amount,
            tax=0,  # Add tax calculation if needed
            payment_status="unpaid"
        )
        db.session.add(invoice)
        db.session.flush()

        for invoice_product in invoice_products:
            invoice_product.invoice_id = invoice.id
            db.session.add(invoice_product)

        db.session.commit()
        logger.info(f"Order {order.id} created with Invoice {invoice.id}")
        return jsonify({"message": "Order created successfully", "order_id": order.id, "invoice_id": invoice.id}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create order: {e}")
        return jsonify({"error": "Failed to create order"}), 400

@order_routes.route("/orders", methods=["GET"])
def get_orders():
    try:
        # Fetch all orders from the database
        orders = Order.query.all()

        # Construct the response
        response = []
        for order in orders:
            # Fetch associated order products
            order_products = OrderProduct.query.filter_by(order_id=order.id).all()

            # Fetch associated invoice for the order
            invoice = Invoice.query.filter_by(order_id=order.id).first()
            invoice_products = InvoiceProduct.query.filter_by(invoice_id=invoice.id).all() if invoice else []

            # Fetch product details for each order product
            products = []
            for order_product in order_products:
                product = Product.query.get(order_product.product_id)
                individual_price = 0
                total_price = 0

                # Find corresponding invoice product to get individual price
                for invoice_product in invoice_products:
                    if invoice_product.product_id == order_product.product_id:
                        individual_price = invoice_product.price_at_time_of_purchase
                        total_price = invoice_product.total_price
                        break

                products.append({
                    "product_id": order_product.product_id,
                    "quantity": order_product.quantity,
                    "individual_price": individual_price,  # Price of each product at the time of purchase
                    "total_price": total_price,  # Total price for this product (quantity * price)
                    "product_details": {
                        "name": product.name if product else None,
                        "description": product.description if product else None,
                        "category": product.category if product else None,
                        # Include other fields as needed
                    }
                })

            # Add the order with its products to the response
            response.append({
                "id": order.id,
                "customer_email": order.customer_email,
                "delivery_address": order.delivery_address,
                "delivery_time_slot": order.delivery_time_slot,
                "payment_method": order.payment_method,
                "status": order.status,
                "products": products,
            })

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Failed to retrieve orders: {e}")
        return jsonify({"error": "Failed to retrieve orders"}), 500
 


@order_routes.route("/edit_order/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    try:
        order = Order.query.get(order_id)
        print('a')
        # Check if the order exists
        if not order:
            logger.error("Order not found")
            return jsonify({"error": "Order not found"}), 404

        # Fetch the associated invoice
        invoice = Invoice.query.filter_by(order_id=order.id).first()
        # Calculate price field based on user tier
        user = User.query.get(order.customer_email)
        if not user:
            logger.error("User not found")
            return jsonify({"error": "User not found"}), 404

        price_tier_map = {"gold": "gold_price", "premium": "premium_price", "basic": "regular_price"}
        user_tier = user.tier.lower() if user and user.tier else "regular"
        price_field = price_tier_map.get(user_tier, "regular_price")

        # Update fields that are directly on the Order
        data = request.json
        if "delivery_time_slot" in data:
            delivery_time_slot= data["delivery_time_slot"].lower()
            valid_delivery_time_slot = ["morning", "afternoon", "evening"]

            if delivery_time_slot not in valid_delivery_time_slot:
                logger.error("Invalid delivery time slot value")
                return jsonify({"error": "Invalid delivery time slot value"}), 400
            order.delivery_time_slot = data["delivery_time_slot"]
        if "delivery_address" in data:
            delivery_address = data["delivery_address"]

            # Check if the current address is an in-store pickup
            instore_pickup_locations = ["ABC Verdun", "ABC Ashrafieh", "ABC Dbayeh"]

            if delivery_address in instore_pickup_locations:
                # Validate the new in-store pickup location
                if delivery_address not in instore_pickup_locations:
                    logger.error("Invalid in-store pickup location")
                    return jsonify({"error": f"Invalid in-store pickup location. Valid locations are: {', '.join(instore_pickup_locations)}"}), 400

                # Update the in-store pickup location
                order.delivery_address = delivery_address
                logger.info(f"Updated in-store pickup location to {delivery_address}")
            else:
                # Validate delivery address for non-in-store orders
                address_pattern = r"^[a-zA-Z\s]+-[a-zA-Z\s]+-[a-zA-Z0-9\s]+-[0-9\s]+$"
                if not re.match(address_pattern, delivery_address):
                    logger.error("Delivery address format is invalid. Expected format: City-Street-Building-Floor.")
                    return jsonify({"error": "Delivery address format is invalid. Expected format: City-Street-Building-Floor."}), 400

                order.delivery_address = delivery_address
        if "status" in data:
            new_status = data["status"].lower()  # Ensure consistent casing
            valid_statuses = ["pending", "processing", "shipped", "delivered"]

            if new_status not in valid_statuses:
                logger.error("Invalid status value")
                return jsonify({"error": "Invalid status value"}), 400

            # Define the status transition order
            status_order = {
                "pending": 0,
                "processing": 1,
                "shipped": 2,
                "delivered": 3
            }

            current_status = order.status.lower() if order.status else "pending"

            # Log current and new status for debugging
            logger.info(f"Current status: {current_status}, New status: {new_status}")

            # Check if the current status is valid
            if current_status not in status_order:
                logger.error(f"Current status '{current_status}' is invalid.")
                return jsonify({"error": f"Current status '{current_status}' is invalid."}), 400

            # Check if the new status follows the correct sequence
            if status_order[new_status] < status_order[current_status]:
                logger.error(f"Cannot update status to {new_status}. Status update must be incremental.")
                return jsonify({"error": f"Cannot update status to {new_status}. Status update must be incremental."}), 400

            # Update the order status
            order.status = new_status

        
        # Handle products in the order
        if "products" in data:
            for product_data in data["products"]:
                product_id = product_data.get("product_id")
                quantity =int(product_data.get("quantity"))

                # Validate that the quantity is positive or zero
                if quantity < 0:
                    logger.info("Quantity cannot be negative")
                    return jsonify({"error": "Quantity cannot be negative"}), 400

                if product_id:
                    # Check if the product is already associated with the order
                    existing_order_product = OrderProduct.query.filter_by(order_id=order.id, product_id=product_id).first()

                    if existing_order_product:
                        if quantity == 0:
                            # If the quantity is 0, remove the product from the order
                            db.session.delete(existing_order_product)

                            # Restore the quantity in the WarehouseProduct table
                            warehouse_product = WarehouseProduct.query.filter_by(product_id=product_id).first()
                            if warehouse_product:
                                warehouse_product.quantity += existing_order_product.quantity

                            # Remove the product from the invoice
                            if invoice:
                                invoice_product = InvoiceProduct.query.filter_by(
                                    invoice_id=invoice.id, product_id=product_id
                                ).first()
                                if invoice_product:
                                    db.session.delete(invoice_product)
                        else:
                            # Update the quantity of an existing product
                            difference = quantity - existing_order_product.quantity
                            existing_order_product.quantity = quantity

                            # Update the stock in the WarehouseProduct table by the difference
                            warehouse_product = WarehouseProduct.query.filter_by(product_id=product_id).first()
                            if warehouse_product:
                                new_quantity = warehouse_product.quantity - difference
                                if new_quantity < 0:
                                    db.session.rollback()
                                    logger.info(f"Not enough stock for product ID {product_id}")
                                    return jsonify({"error": f"Not enough stock for product ID {product_id}"}), 400
                                warehouse_product.quantity = new_quantity

                            # Update the invoice product
                            if invoice:
                                invoice_product = InvoiceProduct.query.filter_by(
                                    invoice_id=invoice.id, product_id=product_id
                                ).first()
                                if invoice_product:
                                    product = Product.query.get(product_id)
                                    product_price = getattr(product, price_field, 0) or 0
                                    if product.discount:
                                        product_price -= product_price * (product.discount / 100)
                                    invoice_product.quantity = quantity
                                    invoice_product.total_price = product_price * quantity
                    else:
                        if quantity > 0:
                            # Add a new product to the order
                            new_order_product = OrderProduct(order_id=order.id, product_id=product_id, quantity=quantity)
                            db.session.add(new_order_product)

                            # Decrease the quantity in the WarehouseProduct table
                            warehouse_product = WarehouseProduct.query.filter_by(product_id=product_id).first()
                            if warehouse_product:
                                new_quantity = warehouse_product.quantity - quantity
                                if new_quantity < 0:
                                    db.session.rollback()
                                    logger.info(f"Insufficient stock for product ID {product_id}")
                                    return jsonify({"error": f"Insufficient stock for product ID {product_id}"}), 400
                                warehouse_product.quantity = new_quantity

                            # Add the product to the invoice
                            if invoice:
                                product = Product.query.get(product_id)
                                product_price = getattr(product, price_field, 0) or 0
                                if product.discount:
                                    product_price -= product_price * (product.discount / 100)
                                new_invoice_product = InvoiceProduct(
                                    invoice_id=invoice.id,
                                    product_id=product_id,
                                    quantity=quantity,
                                    price_at_time_of_purchase=product_price,
                                    total_price=product_price * quantity
                                )
                                db.session.add(new_invoice_product)
        
        # Recalculate the invoice total
        if invoice:
            invoice_products = InvoiceProduct.query.filter_by(invoice_id=invoice.id).all()
            invoice.total_amount = sum(p.total_price for p in invoice_products)

        db.session.commit()
        logger.info(f"Order {order_id} and associated invoice updated successfully")
        return jsonify({"message": "Order and invoice updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logger.warning(f"Failed to update order {order_id}: {e}")
        return jsonify({"error": "Failed to update order"}), 400


@order_routes.route("/delete_order/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    try:
        # Fetch the order by ID
        order = Order.query.get(order_id)
        if not order:
            logger.warning(f"Order with ID {order_id} not found.")
            return jsonify({"error": "Order not found"}), 404

        # Fetch associated order products
        order_products = OrderProduct.query.filter_by(order_id=order.id).all()

        # Restore stock for each product in the order
        for order_product in order_products:
            warehouse_product = WarehouseProduct.query.filter_by(product_id=order_product.product_id).first()
            if warehouse_product:
                warehouse_product.quantity += order_product.quantity
            db.session.delete(order_product)  # Delete the order-product association

        # Delete associated invoice and its products
        invoice = Invoice.query.filter_by(order_id=order.id).first()
        if invoice:
            invoice_products = InvoiceProduct.query.filter_by(invoice_id=invoice.id).all()
            for invoice_product in invoice_products:
                db.session.delete(invoice_product)  # Delete the invoice-product association
            db.session.delete(invoice)  # Delete the invoice itself

        # Finally, delete the order
        db.session.delete(order)
        db.session.commit()

        logger.info(f"Order {order_id} and associated data deleted successfully.")
        return jsonify({"message": f"Order {order_id} deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete order {order_id}: {e}")
        return jsonify({"error": "Failed to delete order"}), 500



@order_routes.route("/invoices", methods=["GET"])
def get_invoices():
    try:
        # Query all invoices
        invoices = Invoice.query.all()

        # Manually construct the response
        response = []
        for invoice in invoices:
            # Fetch associated invoice_products
            invoice_products = InvoiceProduct.query.filter_by(invoice_id=invoice.id).all()

            # Fetch product details for each invoice_product
            products = []
            for invoice_product in invoice_products:
                product = Product.query.get(invoice_product.product_id)
                products.append({
                    "product_id": invoice_product.product_id,
                    "quantity": invoice_product.quantity,
                    "price_at_time_of_purchase": invoice_product.price_at_time_of_purchase,
                    "total_price": invoice_product.total_price,
                    "product_details": {
                        "name": product.name if product else None,
                        "description": product.description if product else None,
                        "category": product.category if product else None,
                        # Include other fields as needed
                    }
                })

            # Add the invoice with its products to the response
            response.append({
                "id": invoice.id,
                "order_id": invoice.order_id,
                "invoice_date": invoice.invoice_date,
                "total_amount": invoice.total_amount,
                "tax": invoice.tax,
                "payment_status": invoice.payment_status,
                "products": products
            })

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Failed to retrieve invoices: {e}")
        return jsonify({"error": "Failed to retrieve invoices"}), 500

@order_routes.route("/get_invoice/<int:invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    try:
        # Fetch the invoice by ID
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            logger.warning(f"Invoice with ID {invoice_id} not found.")
            return jsonify({"error": "Invoice not found"}), 404

        # Fetch associated invoice_products
        invoice_products = InvoiceProduct.query.filter_by(invoice_id=invoice.id).all()

        # Fetch product details for each invoice_product
        products = []
        for invoice_product in invoice_products:
            product = Product.query.get(invoice_product.product_id)
            products.append({
                "product_id": invoice_product.product_id,
                "quantity": invoice_product.quantity,
                "price_at_time_of_purchase": invoice_product.price_at_time_of_purchase,
                "total_price": invoice_product.total_price,
                "product_details": {
                    "name": product.name if product else None,
                    "description": product.description if product else None,
                    "category": product.category if product else None,
                    # Add additional product fields as needed
                }
            })

        # Construct the response
        response = {
            "id": invoice.id,
            "order_id": invoice.order_id,
            "invoice_date": invoice.invoice_date,
            "total_amount": invoice.total_amount,
            "tax": invoice.tax,
            "payment_status": invoice.payment_status,
            "products": products
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Failed to retrieve invoice {invoice_id}: {e}")
        return jsonify({"error": "Failed to retrieve invoice"}), 500
    
@order_routes.route("/update_invoice_payment/<int:invoice_id>", methods=["PUT"])
def update_invoice_payment(invoice_id):
    try:
        # Retrieve the invoice by ID
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            logger.warning(f"Invoice with ID {invoice_id} not found.")
            return jsonify({"error": "Invoice not found"}), 404

        # Get the payment status from the request payload
        data = request.get_json()
        if not data or "payment_status" not in data:
            logger.warning("Payment status not provided in request.")
            return jsonify({"error": "Payment status is required"}), 400

        payment_status = data["payment_status"].lower()

        # Validate the provided payment status
        valid_statuses = ["unpaid", "partial", "paid"]
        if payment_status not in valid_statuses:
            logger.warning(f"Invalid payment status: {payment_status}")
            return jsonify({"error": f"Invalid payment status. Valid statuses are: {', '.join(valid_statuses)}"}), 400

        # Define the allowed transitions
        status_transitions = {
            "unpaid": ["partial", "paid"],
            "partial": ["paid"],
            "paid": []  # No transitions allowed from "paid"
        }

        # Check if the new status is a valid transition
        current_status = invoice.payment_status.lower()
        if payment_status not in status_transitions[current_status]:
            logger.warning(
                f"Invalid payment status transition from '{current_status}' to '{payment_status}'."
            )
            return jsonify({
                "error": f"Cannot change payment status from '{current_status}' to '{payment_status}'."
            }), 400

        # Update the payment status
        logger.info(f"Updating payment status of Invoice ID {invoice_id} to '{payment_status}'.")
        invoice.payment_status = payment_status

        # Commit the changes to the database
        db.session.commit()

        return jsonify({
            "message": "Payment status updated successfully",
            "invoice": {
                "id": invoice.id,
                "order_id": invoice.order_id,
                "payment_status": invoice.payment_status
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to update payment status for Invoice {invoice_id}: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to update payment status"}), 500



@order_routes.route("/returns", methods=["GET"])
def get_returns():
    try:
        returns = Return.query.all()
        response = []
        for ret in returns:
            response.append({
                "id": ret.id,
                "order_id": ret.order_id,
                "product_id": ret.product_id,
                "quantity_to_be_returned":ret.quantity_to_be_returned,
                "customer_email": ret.customer_email,
                "reason": ret.reason,
                "status": ret.status,
                "refund_amount": ret.refund_amount,
                "requested_date": ret.requested_date,
                "approved_date": ret.approved_date
            })
        logger.error(f"Success in fetching return requests.")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Failed to fetch return requests: {e}")
        return jsonify({"error": "Failed to fetch return requests"}), 500
    
@order_routes.route("/update_return_status/<int:return_id>", methods=["PUT"])
def update_return_status(return_id):
    try:
        # Fetch the return request by ID
        ret = Return.query.get(return_id)
        if not ret:
            logger.warning(f"Return request with ID {return_id} not found.")
            return jsonify({"error": "Return request not found"}), 404

        data = request.get_json()
        if not data or "status" not in data:
            logger.warning("Status is required in the request.")
            return jsonify({"error": "Status is required"}), 400

        status = data["status"].lower()
        if status not in ["approved", "denied"]:
            logger.warning(f"Invalid status: {status}")
            return jsonify({"error": "Invalid status. Valid statuses are 'approved' and 'denied'"}), 400

        # Disallow transitioning from approved to denied
        if ret.status == "approved" and status == "denied":
            logger.warning(f"Attempt to deny a return request already approved (ID: {return_id}).")
            return jsonify({"error": "Cannot deny a return request that has already been approved."}), 400

        refund_amount = None  # Default value for refund_amount

        if status == "approved":
            refund_amount = data.get("refund_amount")

            # Validate and handle refund_amount
            if refund_amount is None or refund_amount == '':
                logger.warning(f"Refund amount is missing or invalid for return request {return_id}.")
                return jsonify({"error": "Refund amount is required for approval."}), 400
            
            try:
                refund_amount = float(refund_amount)
                if refund_amount < 0:
                    raise ValueError("Refund amount cannot be negative.")
            except ValueError as e:
                logger.warning(f"Invalid refund amount for return request {return_id}: {e}")
                return jsonify({"error": "Refund amount must be a valid non-negative number."}), 400

            # Fetch user and product details
            user = User.query.filter_by(email=ret.customer_email).first()
            product = Product.query.get(ret.product_id)
            if not user:
                logger.warning(f"User with email {ret.customer_email} not found.")
                return jsonify({"error": "User not found for return request."}), 404
            if not product:
                logger.warning(f"Product with ID {ret.product_id} not found.")
                return jsonify({"error": "Product not found for return request."}), 404

            # Determine price based on user's tier
            tier_price_map = {"basic": "regular_price", "gold": "gold_price", "premium": "premium_price"}
            user_tier = user.tier.lower() if user.tier else "basic"
            price_field = tier_price_map.get(user_tier, "regular_price")
            product_price = getattr(product, price_field, None)

            if product_price is None:
                logger.warning(f"Product price not available for user tier {user_tier}.")
                return jsonify({"error": f"Product price not found for user tier '{user_tier}'."}), 400

            # Calculate total expected refund amount
            expected_refund_amount = product_price * ret.quantity_to_be_returned
            if refund_amount != expected_refund_amount:
                logger.warning(f"Refund amount mismatch: expected {expected_refund_amount}, got {refund_amount}.")
                return jsonify({
                    "error": f"Refund amount does not match the expected value of {expected_refund_amount:.2f}."
                }), 400

            # Update the return request
            ret.status = "approved"
            ret.approved_date = datetime.datetime.utcnow()
            ret.refund_amount = refund_amount
        else:
            ret.status = "denied"

        db.session.commit()
        logger.info(f"Return request {return_id} updated to status '{status}' with refund amount '{refund_amount}'")
        return jsonify({"message": "Return status updated successfully"}), 200

    except Exception as e:
        logger.error(f"Failed to update return status for request {return_id}: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to update return status"}), 500
