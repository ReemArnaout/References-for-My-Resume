from app import logger, db
from flask import abort, jsonify, request, Blueprint, make_response, current_app
import requests
from sqlalchemy import text
from model.employee import Employee
from model.roles import Roles

employee_management_routes = Blueprint("employee_management_routes", __name__)

@employee_management_routes.route("/add_employee", methods = ["POST"])
def add_employee():
    try:
        data = request.json
        email = data["email"]
        password = data["password"]
        first_name = data["first_name"]
        last_name = data["last_name"]
        e = Employee(email, password, first_name, last_name)
        db.session.add(e)
        db.session.commit()
        return jsonify({"message": "added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.warning(e)
        abort(500)


@employee_management_routes.route("/delete_employee", methods = ["DELETE"])
def delete_employee():
    email = request.args.get("email")
    try:
        db.session.execute(text("delete from secureglow.employee where email = :email"), {'email': email})
        db.session.commit()
        return jsonify({"message": "deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        abort (500)

@employee_management_routes.route("/add_role", methods=["POST"])
def add_role():
    email = request.json["email"]
    role = request.json["role"]
    r = Roles(email, role)
    try:
        db.session.add(r)
        db.session.commit()
        return jsonify({"message": "role added successfully"}), 201
    except:
        db.session.rollback()
        abort (500)

@employee_management_routes.route("/delete_role", methods = ["DELETE"])
def delete_role():
    email = request.args.get("email")
    role = request.args.get("role")
    print(email, role)
    try:
        db.session.execute(text("delete from secureglow.roles where email = :email and role = :role"), {'email': email, 'role': role})
        db.session.commit()
        return jsonify({"message": "deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        abort (500)