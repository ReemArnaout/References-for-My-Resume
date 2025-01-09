import sys
sys.path.append("..") 
from app import db, ma, datetime, hasher

class VerificationCode(db.Model): 
    email = db.Column(db.String(30), db.ForeignKey('employee.email', ondelete='CASCADE'), primary_key=True) 
    hashed_code = db.Column(db.String(128)) 
    expiry_date = db.Column(db.DateTime) 
    attempts = db.Column(db.Integer)
    def __init__(self, email, code): 
        super(VerificationCode, self).__init__(email=email, expiry_date=datetime.datetime.utcnow() + datetime.timedelta(minutes=5)) 
        self.hashed_code = hasher.hash(code)
        self.attempts = 3

class VerificationCodeSchema(ma.Schema): 
    class Meta: 
        fields = ("email", "expiry_date", "attempts") 
        model = VerificationCode

verification_code_schema = VerificationCodeSchema() 