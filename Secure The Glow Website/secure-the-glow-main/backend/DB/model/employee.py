import sys
sys.path.append("..") 
from app import ma, db, datetime, hasher

class Employee(db.Model): 
    email = db.Column(db.String(30), primary_key=True) 
    hashed_password = db.Column(db.String(128)) 
    first_name = db.Column(db.String(30)) 
    last_name = db.Column(db.String(30)) 
    login_attempts = db.Column(db.Integer)
    lockout_date = db.Column(db.DateTime) 
    def __init__(self, email, password, first_name, last_name): 
        super(Employee, self).__init__(email=email, first_name = first_name, last_name = last_name) 
        self.hashed_password = hasher.hash(password)
        self.login_attempts = 7
        self.lockout_date = datetime.datetime.utcnow() - datetime.timedelta(minutes=20)

class EmployeeSchema(ma.Schema): 
    class Meta: 
        fields = ("email", "first_name", "last_name") 
        model = Employee 

employee_schema = EmployeeSchema() 