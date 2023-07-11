from app import app
from db_config import mysql
from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re
import datetime as dt
import csv

ALLOW_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOW_EXTENSIONS

@app.route('/')
def dashboard():
    return render_template('login.html')

@app.route('/login', method=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
        users = cursor.fetchone()
        if users:
            session['loggedin'] = True
            session['id'] = users['id']
            session['username'] = users['username']
            msg = 'Logged in Successfully !'
            return render_template('menu.html', msg = msg)
        elif not check_password_hash(users['password'], password):
            msg = 'Incorrect Password'
        else:
            msg = 'Incorrect username/password'
    return render_template('login.html', msg = msg)

@app.route('/register', method=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'username' in request.form and 'password' in request.form and 'phone' in request.form:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
        users = cursor.fetchone()
        if users:
            msg = 'Account already exist !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', username):
            msg = 'Invalid username !'
        elif not username or not password or not username:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s, % s, % s, 2)', (first_name, last_name, username, generate_password_hash(password), phone_number, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/menu')
def home():
    return render_template('menu.html')

@app.route('/file_upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        resp = jsonify({'message': 'No File part in the request'})
        resp.status_code = 400
        return resp
    
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No File selected for uploading'})
        resp.status_code = 400
        return resp
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the CSV file and unmarshal data into the database
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # Assuming you have a database model called 'DataModel'
                data = DataModel(column1=row['nama'], column2=row['pengetahuan semester 1'], column3=row['keterampilan semester 1'], column4=row['pengetahuan semester 2'], column5=row['keterampilan semester 2'])
                db.session.add(data)
            db.session.commit()
        
        resp = jsonify({'message': 'File successfully uploaded and data unmarshalled into the database'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are csv'})
        resp.status_code = 400
        return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)