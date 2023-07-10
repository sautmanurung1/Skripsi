from app import app
from flask_mysqldb import MySQL

mysql = MySQL()

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sautmanurung234'
app.config['MYSQL_DB'] = ''

mysql.init_app(app)