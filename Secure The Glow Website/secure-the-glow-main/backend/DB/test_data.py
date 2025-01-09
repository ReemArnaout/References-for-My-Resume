from app import db, app
from app import Employee, Roles
def insert_employees(mail, passwd, fname, lname, role):
    with app.app_context():
        e = Employee(mail, passwd, fname, lname)
        r = Roles(mail, role)
        db.session.add(e)
        db.session.add(r)
        db.session.commit()

#EMAILS FOR EACH USER AND THEIR CORRESPONDING ROLES. THEY ALL HAVE THE SAME PASSWORD, FIRSTNAME, LASTNAME FOR SIMPLICITY
ROLES = ['super-admin', "business-manager", 'stocking-employee', "marketing-analyst", "customer-service-specialist", "logistics-employee"]
emails = ['superman@mail.com','joe@mail.com', 'bob@mail.com', 'jane@mail.com', 'walter@mail.com', 'skylar@mail.com']
if __name__ == '__main__':
    for i in range(6):
        insert_employees(emails[i], 'Q1@werty', 'joe', 'doe', ROLES[i])

#python test_data.py