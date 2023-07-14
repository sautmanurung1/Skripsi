from app import app
from db_config import mysql
from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import MySQLdb.cursors
import re
import datetime as dt
import csv
import os
from os.path import join, dirname, realpath
from sklearn.metrics import pairwise_distances
from sklearn_extra.cluster import KMedoids
import pandas as pd
import numpy as np

UPLOAD_FOLDER_DATA_NILAI = 'static/uploads/dataNilai'
app.config['UPLOAD_FOLDER_DATA_NILAI'] = UPLOAD_FOLDER_DATA_NILAI

UPLOAD_FOLDER_DATA_SISWA = 'static/uploads/dataSiswa'
app.config['UPLOAD_FOLDER_DATA_SISWA'] = UPLOAD_FOLDER_DATA_SISWA


@app.route('/')
def dashboard():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/register', methods=['GET', 'POST'])
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


@app.route('/datasiswa')
def datasiswa():
    return render_template('datasiswa.html')


@app.route('/datanilai')
def datanilai():
    return render_template('datanilai.html')


@app.route('/file_upload-data-nilai', methods=['POST'])
def upload_file():
    # get the uploaded file
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER_DATA_NILAI'], uploaded_file.filename)
        # set the file path
        uploaded_file.save(file_path)
        parseCSVDatanilai(file_path)
        # save the file
    return redirect(url_for('home'))


@app.route('/file_upload-data-siswa', methods=['POST'])
def upload_file_data_siswa():
    uploaded_file_data_siswa = request.files['file']
    if uploaded_file_data_siswa.filename != '':
        file_path_data_siswa = os.path.join(app.config['UPLOAD_FOLDER_DATA_SISWA'], uploaded_file_data_siswa.filename)
        # set the file path
        uploaded_file_data_siswa.save(file_path_data_siswa)
        parseCSVDatasiswa(file_path_data_siswa)
        # save the file
    return redirect(url_for('home'))


@app.route('/fetch_data-nilai')
def fetch_data_nilai():
     # Retrieve data from the database
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM data_nilai"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()

    # Convert the data into a list of dictionaries
    data_list = []
    for row in data:
        data_dict = {
            'no': row[0],
            'nis': row[1],
            'nama': row[2],
            'pengetahuan_semester_1': row[3],
            'keterampilan_semester_1': row[4],
            'pengetahuan_semester_2': row[5],
            'keterampilan_semester_2': row[6]
        }
        data_list.append(data_dict)
    return jsonify(data_list)


@app.route('/fetch_data-siswa')
def fetch_data_siswa():
     # Retrieve data from the database
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM data_siswa"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()

    # Convert the data into a list of dictionaries
    data_list = []
    for row in data:
        data_dict = {
            'no': row[0],
            'nis': row[1],
            'nama': row[2],
            'jenis_kelamin': row[3],
            'kelas_awal': row[4]
        }
        data_list.append(data_dict)
    return jsonify(data_list)


def parseCSVDatanilai(filePath):
      # CVS Column Names
      col_names = ['no','nama', 'pengetahuan_semester_1', 'keterampilan_semester_1' , 'pengetahuan_semester_2', 'keterampilan_semester_2']
      # Use Pandas to parse the CSV file
      csvData = pd.read_csv(filePath,names=col_names, header=None)
      # Loop through the Rows
      for i,row in csvData.iterrows():
             sql = "INSERT INTO data_nilai (no, nama, pengetahuan_semester_1, keterampilan_semester_1, pengetahuan_semester_2, keterampilan_semester_2) VALUES (NULL, % s, % s, % s, % s, % s)"
             value = (
                        str(row['nama']),
                        str(row['pengetahuan_semester_1']),
                        str(row['keterampilan_semester_1']),
                        str(row['pengetahuan_semester_2']),
                        str(row['keterampilan_semester_2'])
                    )
             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
             cursor.execute(sql, value)
             mysql.connection.commit()


def parseCSVDatasiswa(filePath):
      # CVS Column Names
      col_names = ['No','Nama', 'Jenis Kelamin', 'Kelas Awal']
      # Use Pandas to parse the CSV file
      csvData = pd.read_csv(filePath, names=col_names, header=None)
      # Loop through the Rows
      for i,row in csvData.iterrows():
             sql = "INSERT INTO data_siswa (no, nama, jenis_kelamin, kelas_awal) VALUES (NULL, % s, % s, % s)"
             value = (
                        str(row['Nama']),
                        str(row['Jenis Kelamin']),
                        str(row['Kelas Awal'])
                    )
             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
             cursor.execute(sql, value)
             mysql.connection.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)