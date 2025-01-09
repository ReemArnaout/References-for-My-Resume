from flask import Flask, request, make_response, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect, generate_csrf ### To use for CSRF Protection
from flask_mail import Mail
from dotenv import load_dotenv
import os
import logging 


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)


load_dotenv()
EMAIL_PASS = str(os.getenv('EMAIL_PASS'))
app.config['SECRET_KEY'] = str(os.getenv('SECRET_KEY'))
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ayaalbaba7@gmail.com'
app.config['MAIL_PASSWORD'] = EMAIL_PASS
app.config['MAIL_DEFAULT_SENDER'] = 'ayaalbaba7@gmail.com' # https://mailtrap.io/blog/flask-send-email-gmail/



from authentication import auth_routes, token_required
from products import product_routes
from orders import order_routes
from inventory import inventory_routes 
from employee_management import employee_management_routes


@app.route('/csrf-token', methods=['GET'])
@token_required
def get_csrf_token(email, roles):
    return jsonify({'csrf_token': generate_csrf()})

app.register_blueprint(auth_routes)
app.register_blueprint(product_routes)
app.register_blueprint(order_routes)
app.register_blueprint(inventory_routes)
app.register_blueprint(employee_management_routes)

# Limit the file size to 10MB (10 * 1024 * 1024 bytes)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

##app.config['TESTING'] = True ############################ REMOVE THESE WHEN DONE WITH TESTING
#app.config['WTF_CSRF_ENABLED'] = False #################
mail = Mail(app)


if __name__ == '__main__':
    app.run(port=5002) 