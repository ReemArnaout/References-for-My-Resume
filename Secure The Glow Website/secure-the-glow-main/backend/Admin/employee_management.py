from app import logger, csrf
from flask import abort, jsonify, request, Blueprint
from authentication import token_required
import requests
import re
from werkzeug.exceptions import BadRequest


def check_password_strength(pwd):
    # Criteria checks
    length_criteria = len(pwd) >= 8
    uppercase_criteria = re.search(r'[A-Z]', pwd) is not None
    lowercase_criteria = re.search(r'[a-z]', pwd) is not None
    digit_criteria = re.search(r'\d', pwd) is not None
    special_char_criteria = re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd) is not None

    # All criteria must be met
    is_strong = (
        length_criteria and
        uppercase_criteria and
        lowercase_criteria and
        digit_criteria and
        special_char_criteria
    )
    
    return is_strong

employee_management_routes = Blueprint("employee_management_routes", __name__)

def validate_input(email, password, first_name, last_name):
    # Validate Email
    if not email:
        raise BadRequest("Email is required.")
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_pattern, email):
        raise BadRequest("Invalid email format.")
    if not first_name:
        raise BadRequest("First name is required.")
    if not re.match(r"^[A-Za-z]+$", first_name):
        raise BadRequest("First name can only contain letters.")
    if not check_password_strength(password):
        raise BadRequest("bad password.")
    # Validate Last Name
    if not last_name:
        raise BadRequest("Last name is required.")
    if not re.match(r"^[A-Za-z]+$", last_name):
        raise BadRequest("Last name can only contain letters.")
    
    return email, password, first_name, last_name

@employee_management_routes.route("/add_employee", methods = ["POST"])
@token_required
@csrf.exempt
def add_employee(email, roles):
    if "super-admin" not in roles:
        logger.warning(f" unauthorized attempt by {email} to add employee")
        abort(403)
    try:
        url = "http://localhost:5001/add_employee"
        data = request.json
        email = data["email"]
        password = data["password"]
        first_name = data["first_name"]
        last_name = data["last_name"]
        validate_input(email, password, first_name, last_name)
        response = requests.post(url, json=data)
        if response.status_code == 201:
            return jsonify({"message": "added successfully"}), 201
        abort(response.status_code)
    except Exception as e:
        logger.error(e)
        abort(500)


@employee_management_routes.route("/delete_employee", methods = ["DELETE"])
@token_required
@csrf.exempt
def delete_employee(mail, roles):
    if "super-admin" not in roles:
        logger.warning(f" unauthorized attempt by {mail} to delete employee")
        abort(403)
    email = request.args.get("email")
    
    if not email:
        raise BadRequest("Email is required.")
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_pattern, email):
        raise BadRequest("Invalid email format.")
    
    url = "http://localhost:5001/delete_employee?email="+email
    response = requests.delete(url=url)
    if response.status_code == 200:
        logger.info(f"{email} deleted by {mail}")
        return jsonify({"message": "deleted successfully"}), 200
    abort(response.status_code)

ROLES = ["business-manager", 'stocking-employee', "marketing-analyst", "customer-service-specialist", "logistics-employee"]

@employee_management_routes.route("/add_role", methods=["POST"])
@token_required
@csrf.exempt
def add_role(mail, roles):
    if "super-admin" not in roles:
        logger.warning(f" unauthorized attempt by {mail} to delete employee")
        abort(403)
    try:
        email = request.json["email"]
        role = request.json["role"]
        if not email:
            raise BadRequest("Email is required.")
        email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_pattern, email):
            raise BadRequest("Invalid email format.")
        if role not in ROLES:
            abort(400)
        url = "http://localhost:5001/add_role"
        response = requests.post(url, json=request.json)
        if response.status_code == 201:
            logger.info(f"{email} deleted by {mail}")
            return jsonify({"message": "role added successfully"}), 201
        abort(response.status_code)

    except:
        abort(500)

@employee_management_routes.route("/delete_role", methods = ["DELETE"])
@token_required
@csrf.exempt
def delete_role(mail, roles):
    if "super-admin" not in roles:
        logger.warning(f" unauthorized attempt by {mail} to delete employee")
        abort(403)
    try:
        email = request.args.get("email")
        role = request.args.get("role")
        if not email:
            raise BadRequest("Email is required.")
        email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_pattern, email):
            raise BadRequest("Invalid email format.")
        if role not in ROLES:
            abort(400)
        
        url = "http://localhost:5001/delete_role?email="+email+"&role="+role
        response = requests.delete(url)
        if response.status_code == 200:
            logger.info(f"{email} deleted by {mail}")
            return jsonify({"message": "role deleted successfully"}), 200
        abort(response.status_code)

    except Exception as e:
        logger.error(e)
        abort(500)