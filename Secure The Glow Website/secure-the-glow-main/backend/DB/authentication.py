from app import logger, db, hasher, text, Blueprint, datetime, argon2
from model.employee import Employee, employee_schema 
from model.roles import Roles, roles_schema 
from model.verification_codes import VerificationCode
from flask import request, jsonify, abort

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/authenticate_employee', methods=['GET'])
def authenticate_employee():
    email = request.json.get('email')
    password = request.json.get('password')
    employee = db.session.execute(text(f"select * from secureglow.employee where email = :email"), {'email': email}).fetchone()
    logger.info(f'Attempted login by {email}')
    try:
        if hasher.verify(employee.hashed_password, password) and datetime.datetime.utcnow() > employee.lockout_date + datetime.timedelta(minutes=15):
                db.session.execute(text(f"UPDATE secureglow.employee set login_attempts = 7 where email = :email"), {'email': email})
                db.session.commit()
                logger.info(f'Successful login by {email} ')
                return jsonify(employee_schema.dump(employee), 200)
        else:
            logger.warning(f'Failed login by {email}. Account locked.')
            print(e)
            abort(403)
            
    except Exception as e:
        try:
            db.session.execute(text(f"UPDATE secureglow.employee set login_attempts = login_attempts - 1 where email = :email"), {'email': email})
            if employee.login_attempts - 1 <= 0:
                db.session.execute(text(f"UPDATE secureglow.employee set lockout_date = :lockout_date where email = :email"), {'email': email, "lockout_date": datetime.datetime.utcnow()})
            db.session.commit()
            logger.warning(f'Wrong password by {email} ')
            abort(403)
        except:
            logger.warning(f'Failed login by {email}')
            print(e)
            abort(403)
        
@auth_routes.route('/employee_roles', methods=["GET"])
def get_roles():
    email = email = request.args.get('email')
    roles = db.session.execute(text(f"select * from secureglow.roles where email = :email"), {'email': email})
    logger.info(f'Requested roles for {email} ')
    return jsonify(roles_schema.dump(roles), 200)

@auth_routes.route('/store_code', methods=["POST"])
def store_code():
    email = request.json["email"]
    code = request.json["code"]
    v = VerificationCode(email, code)
    try:
        db.session.add(v)
        db.session.commit()
        logger.info(f'Generated code for {email} ')
    except Exception as e:
        db.session.rollback()
        try:
            db.session.execute(text('delete from verification_code where email = :email'), {"email" : email})
            db.session.add(v)
            db.session.commit()
            logger.info(f'Generated code for {email} ')
        except:
            db.session.rollback()
            logger.error(f'Failed to generate code for {email} ')
            abort(403)

    return jsonify({"message" : "code successfuly added"}), 201

@auth_routes.route('/change_password', methods=["PUT"])
def change_password():
    code = request.json["code"]
    email = request.json["email"]
    new_password = request.json["password"]
    try:
        verification_row = db.session.execute(text("select * from verification_code where email = :email"), {"email": email}).fetchone()
        if hasher.verify(verification_row.hashed_code, code) and verification_row.attempts > 0 and datetime.datetime.utcnow() <= verification_row.expiry_date:
            db.session.execute(text('delete from verification_code where email = :email'), {"email" : email}) # so it is only used once
            db.session.execute(text(f"UPDATE secureglow.employee set hashed_password = :password where email = :email"), {'email': email, "password": hasher.hash(new_password)})
            db.session.commit()
            logger.info(f'Changed password for {email} ')
            return jsonify({"message" : "password changed successfully"}), 201
        elif datetime.datetime.utcnow() > verification_row.expiry_date:
            logger.warning(f'Failed to change password for {email} (expired code)')
        abort(403)
        
    except argon2.exceptions.VerifyMismatchError:
        db.session.execute(text(f"UPDATE secureglow.verification_code set attempts = attempts - 1 where email = :email"), {'email': email})
        db.session.commit()
        logger.warning(f'Failed to change password for {email} (wrong code)')
        if verification_row.attempts <= 0:
            logger.warning(f'Failed to change password for {email} (code attempts exhausted)')
            
        abort(403)
    except Exception as e:
        logger.error(f'Failed to change password for {email} ({e})')
        abort(403)