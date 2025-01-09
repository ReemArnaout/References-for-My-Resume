import jwt
import datetime
from flask import abort, jsonify, request, Blueprint, make_response, current_app
import requests
from sqlalchemy import text
import os
from flask_cors import cross_origin
from flask_mail import Message
import traceback
import secrets
import string
import re
from app import logger, csrf
from functools import wraps

SECRET_KEY = str(os.getenv('SECRET_KEY'))

def create_token(email, roles): 
    payload = { 
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=2), 
        'iat': datetime.datetime.utcnow(), 
        'sub': email, 
        'roles': roles
    } 
    return jwt.encode( 
        payload, 
        SECRET_KEY, 
        algorithm='HS256' 
    ) 

def extract_auth_token(authenticated_request): 
    auth_header = authenticated_request.headers.get('Authorization') 
    if auth_header: 
        return auth_header.split(" ")[1] 
    else: 
        return None 
def decode_token(token): 
    payload = jwt.decode(token, SECRET_KEY, 'HS256') 
    return payload['sub'] 

auth_routes = Blueprint('auth_routes', __name__)

#Login
@auth_routes.route('/authenticate_employee', methods=['POST'])
@csrf.exempt
def authenticate():
    email = request.json['email']
    password = request.json['password']
    if email=="" or password=="" or type(email)!=str or type(password)!=str:
        logger.error(f'invalid format of credentials')
        abort(400)
    try:
        user_response = requests.get(f'http://localhost:5001/authenticate_employee', json={"email": email, "password": password})
        user_roles_response = requests.get(f'http://localhost:5001/employee_roles?email={email}')
        if user_response.status_code == 200 and user_roles_response.status_code == 200:
            user_roles = user_roles_response.json()
            roles_list = []
            for d in user_roles[0]:
                roles_list.append(d['role'])
            token = create_token(email, roles_list)
            resp = make_response({"message": "authentication successful", "roles": roles_list})
            resp.set_cookie('admin-glow-token', token, 
                                httponly=True, #to prevent javascript from accessing cookie
                                secure=True,    # Only send cookie over HTTPS
                                samesite='Lax' 
                                )
            logger.info(f'Login successful by {email}')
            return resp

        else:
            logger.warning(f'Wrong Login attempt for {email}')
            abort(403)

    except Exception as e:
        logger.error(f'Login error: {e}')
        abort(403)

#Check token validity and extract user info to send them to the client
@auth_routes.route('/employee_info', methods=['GET'])
@csrf.exempt
def get_user_info():
    token = request.cookies.get('admin-glow-token')
    if not token:
        logger.warning(f'No access token provided for get_user_info')
        return jsonify({'message': 'Token is missing!'}), 403

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        roles = data.get('roles')  # Extract roles from the decoded token
        logger.info(f'Sent roles from token successfully')
        return jsonify({'roles': roles}), 200
    except jwt.ExpiredSignatureError:
        logger.warning(f'Expired token')
        return jsonify({'message': 'Token has expired!'}), 403
    except Exception as e:
        logger.warning(f'Invalid token')
        return jsonify({'message': 'Invalid token!'}), 403

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
@auth_routes.route('/forgot_password', methods=['POST'])
@csrf.exempt
def forgot_password(): 
    from app import mail
    verification_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))
    try:
        email = request.json['email']
        url = "http://localhost:5001/store_code" 
        data = {"code": verification_code, "email": email}
        response = requests.post(url, json=data)  
        if response.status_code != 201:
            logger.warning(f'Failed to generate code for {email}')
            return jsonify({'message':"endpoint reached"}), 200
        msg = Message('Password Reset Code', recipients=[email])
        msg.body = f'Your verification code is: {verification_code}'
        mail.send(msg)
        
    except Exception as e:
        logger.error(f'Error generating code for {email}: {e}')
        return jsonify({'message':"endpoint reached"}), 200
        
    logger.info(f'Code sent to {email}')
    return jsonify({'message':"endpoint reached"}), 200

@auth_routes.route('/reset_password', methods=['PUT'])
@csrf.exempt
def reset_password():
    code = request.json["code"]
    email = request.json["email"]
    new_password = request.json["password"]
    if not check_password_strength(new_password):
        logger.warning(f'Weak password by {email}')
        abort(400)
    url = "http://localhost:5001/change_password" 
    data = {"code": code, "email": email, "password": new_password}
    response = requests.put(url, json=data) 
    try:
        message = response.json().get('message')
        msg = Message('Password Reset Successfully', recipients=[email])
        msg.body = f'Your Password was reset successfully'
        from app import mail
        mail.send(msg)
        logger.info(f'Password reset for {email}')
        return jsonify({"message":message}), response.status_code
    except Exception as e:
        logger.warning(f'Error in Password reset for {email}: {e}')
        abort(403)

@auth_routes.route('/logout', methods=['POST'])
@csrf.exempt
def logout():
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.set_cookie('admin-glow-token', '', expires=0)  # Set the JWT cookie to empty and expire it
    response.set_cookie('session', '', expires=0) #Remove the session token that's associated with csrf token
    return response

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.cookies.get('admin-glow-token')
        if not token:
            logger.warning(f"Access to {f} Attempted without token")
            abort(403)
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_email = data['sub']
            roles = data['roles']
        except:
            logger.warning(f"Access to {f} Attempted with bad token")
            abort(403)
        return f(user_email, roles, *args, **kwargs)
    return decorator