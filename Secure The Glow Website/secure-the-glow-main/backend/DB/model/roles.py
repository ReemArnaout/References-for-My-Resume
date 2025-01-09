import sys
sys.path.append("..") 
from app import db, ma

class Roles(db.Model): 
    email = db.Column(db.String(30), db.ForeignKey('employee.email', ondelete='CASCADE'), primary_key=True) 
    role = db.Column(db.String(30), primary_key=True) 
    def __init__(self, email, role): 
        super(Roles, self).__init__(email=email, role = role) 

class RolesSchema(ma.Schema): 
    class Meta: 
        fields = ("email", "role") 
        model = Roles 

roles_schema = RolesSchema(many = True) 