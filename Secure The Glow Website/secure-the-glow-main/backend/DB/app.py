from flask import Flask, jsonify, request, abort, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from db_config import DB_CONFIG
from flask_cors import CORS
from flask_wtf import CSRFProtect ### To use for CSRF Protection
from sqlalchemy import text
import datetime
import traceback
import logging
from argon2 import PasswordHasher
from argon2.low_level import Type
import argon2
from flask_mail import Mail

hasher = PasswordHasher(
    time_cost=2,              # Number of iterations
    memory_cost=19 * 1024,    # Memory in KB (19 MiB here)
    parallelism=1,            # Degree of parallelism
    hash_len=32,              # Desired key length (e.g., 256-bit key for AES-256)
    type=Type.ID               # Specifies Argon2id variant
)


app = Flask(__name__) 
ma = Marshmallow(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
mail = Mail(app)

#csrf = CSRFProtect(app)

app.config[ 'SQLALCHEMY_DATABASE_URI'] =  DB_CONFIG
#CORS(app, resources={r"/*": {"origins": "http://localhost:5002"}}) ### WHITELIST
db = SQLAlchemy(app)

from authentication import auth_routes
from products import product_routes
from orders import order_routes
from inventory import inventory_routes 

from employee_management import employee_management_routes


app.register_blueprint(inventory_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(product_routes)
app.register_blueprint(order_routes)




app.register_blueprint(employee_management_routes)

from model.user import User, user_schema
from model.employee import Employee, employee_schema 
from model.roles import Roles, roles_schema 
from model.verification_codes import VerificationCode
from model.product import Product
from model.product_instance import ProductInstance
from model.product_images import ProductImages
from model.product_ingredients import ProductIngredients
from model.orders import Order, order_schema
from model.returns import Return, return_schema
from model.credit_card_info import CreditCardInfo, credit_card_info_schema
if __name__ == '__main__':
    app.run(port=5001)  