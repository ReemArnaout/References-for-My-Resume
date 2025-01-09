## to create the database: 
1. create a schema called secureglow on mysql  
2. Add a db_config.py file in /backend/DB/, with your database credentials like this : 
DB_CONFIG = "mysql+pymysql://root:_your mysql password_@localhost:3306/secureglow"
3. enter flask shell with the following command in /backend/DB:  
`python -m flask --app app shell`  
then enter the following commands:
```
from app import db 
db.create_all() 
exit()
```

##  to run the backend
1. create a virtual environment in /backend/
2. run the following command `pip install requirements.txt`
3. a .env file is required in backend/admin. It should contain a SECRET_KEY and EMAIL_PASS
4. to run the DB and Admin apps:
```
flask --app DB/app run --port 5001
flask --app Admin/app run --port 5002
```
## insert employees into the database:
we provided a script to insert users with all roles into the database in /backend/DB/test_data.py. run it with the following command ```
python test_data.py
``
This creates five employees, each one with a role.
they all have the password: Q1@werty

## to run the front-end
1. navigate to /admin-frontend/
2. execute the following command `npm install`
3. To run the React App: `npm start`

    