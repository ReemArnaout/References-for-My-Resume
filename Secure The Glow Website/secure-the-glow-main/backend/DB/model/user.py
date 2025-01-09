import sys
sys.path.append("..")
from app import ma, db, datetime, hasher

class User(db.Model):
    __tablename__ = 'users'  # Specify the table name

    email = db.Column(db.String(30), primary_key=True)  # Email as primary key
    tier = db.Column(db.String(10))  
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    login_attempts = db.Column(db.Integer)
    lockout_date = db.Column(db.DateTime)

    def __init__(self, email, tier, password, first_name, last_name, date_of_birth, phone_number=None, address=None):
        # Directly assign values to the fields
        self.email = email
        self.tier = tier
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.hashed_password = hasher.hash(password)  # Hash the password
        self.phone_number = phone_number
        self.address = address
        self.login_attempts = 7
        self.lockout_date = datetime.datetime.utcnow() - datetime.timedelta(minutes=20)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("email", "tier", "first_name", "last_name", "date_of_birth", "hashed_password", "credit_card_info", "phone_number", "address")

user_schema = UserSchema()
