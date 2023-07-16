from app import app
from db_config import mysql
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, make_response
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
import ast
from fpdf import FPDF,HTMLMixin
import html
import io

UPLOAD_FOLDER_DATA_NILAI = 'static/uploads/dataNilai'
app.config['UPLOAD_FOLDER_DATA_NILAI'] = UPLOAD_FOLDER_DATA_NILAI

UPLOAD_FOLDER_DATA_SISWA = 'static/uploads/dataSiswa'
app.config['UPLOAD_FOLDER_DATA_SISWA'] = UPLOAD_FOLDER_DATA_SISWA

UPLOAD_FOLDER_DATA_CLUSTERING = 'static/uploads/dataClustering'
app.config['UPLOAD_FOLDER_DATA_CLUSTERING'] = UPLOAD_FOLDER_DATA_CLUSTERING

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


@app.route('/logout', methods=["GET"])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/menu', methods=["GET"])
def home():
    return render_template('menu.html')


@app.route('/datasiswa', methods=["GET"])
def datasiswa():
    return render_template('datasiswa.html')


@app.route('/datanilai', methods=["GET"])
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


@app.route('/fetch_data-nilai', methods=["GET"])
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


@app.route('/fetch_data-siswa', methods=["GET"])
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


@app.route('/file_upload-data-clustering', methods=['POST'])
def upload_file_data_clustering():
    uploaded_file_data_clustering = request.files['file']
    if uploaded_file_data_clustering.filename != '':
        file_path_data_clustering = os.path.join(app.config['UPLOAD_FOLDER_DATA_CLUSTERING'], uploaded_file_data_clustering.filename)
        uploaded_file_data_clustering.save(file_path_data_clustering)
        parseCSVDataClustering(file_path_data_clustering)
    return redirect(url_for('home'))

def parseCSVDataClustering(filePath):
    data = pd.read_csv(filePath, sep=';')
    
    # Replace commas (,) with periods (.) and convert to float
    data['Peng Sem 1'] = data['Peng Sem 1'].str.replace(',', '.').astype(float)
    data['Peng Sem 2'] = data['Peng Sem 2'].str.replace(',', '.').astype(float)
    data['Ket Sem 1'] = data['Ket Sem 1'].str.replace(',', '.').astype(float)
    data['Ket Sem 2'] = data['Ket Sem 2'].str.replace(',', '.').astype(float)

    # Extract attributes from the data
    attributes = ['Nama', 'Peng Sem 1', 'Ket Sem 1', 'Peng Sem 2', 'Ket Sem 2']
    X = data[attributes].values
    
    # Perform pairwise distance calculation
    distances = pairwise_distances(X[:, 1:], metric='euclidean')

    # Function to calculate the total dissimilarity for a given medoid index
    def total_dissimilarity(index, medoids):
        cluster_indices = np.where(medoids)[0]
        cluster_points = X[cluster_indices]
        cluster_distances = distances[cluster_indices][:, cluster_indices]
        return sum(cluster_distances)

    # Function to find the best medoid with the lowest dissimilarity
    def find_best_medoid(cluster_points, cluster_indices):
        best_medoid = None
        best_dissimilarity = float('inf')
        for i in range(len(cluster_points)):
            dissimilarity = total_dissimilarity(i, cluster_indices)
            if np.all(dissimilarity < best_dissimilarity):
                best_medoid = cluster_indices[i]  # Update with cluster index
                best_dissimilarity = dissimilarity
        return best_medoid, best_dissimilarity

    # Perform K-Medoids clustering
    k = 3  # Number of clusters
    medoids_indices = KMedoids(n_clusters=k, random_state=0).fit_predict(distances)

    # Find the best medoid for each cluster
    medoids = []
    for cluster_id in range(k):
        cluster_indices = np.where(medoids_indices == cluster_id)[0]
        cluster_points = X[cluster_indices]
        medoid_index, _ = find_best_medoid(cluster_points, cluster_indices)
        medoids.append(medoid_index)

    # Retrieve all attributes from data
    all_attributes = X

    # Create a new DataFrame with cluster assignments
    cluster_data = pd.DataFrame(all_attributes, columns=attributes)
    cluster_data['Cluster'] = medoids_indices + 1

    # Divide clusters
    cluster_counts = cluster_data['Cluster'].value_counts()

    # Divide cluster 1 into a, b, c
    cluster_1_data = cluster_data[cluster_data['Cluster'] == 1]
    cluster_1_divided = np.array_split(cluster_1_data, 3)
    a, b, c = cluster_1_divided

    # Add class labels for cluster 1 divisions
    a['Kelas Hasil'] = '7A'
    b['Kelas Hasil'] = '7B'
    c['Kelas Hasil'] = '7C'

    # Divide cluster 2 into d, e, f
    cluster_2_data = cluster_data[cluster_data['Cluster'] == 2]
    cluster_2_divided = np.array_split(cluster_2_data, 3)
    d, e, f = cluster_2_divided

    # Add class labels for cluster 2 divisions
    d['Kelas Hasil'] = '7D'
    e['Kelas Hasil'] = '7E'
    f['Kelas Hasil'] = '7F'

    # Divide cluster 3 into g, h
    cluster_3_data = cluster_data[cluster_data['Cluster'] == 3]
    cluster_3_divided = np.array_split(cluster_3_data, 2)
    g, h = cluster_3_divided

    # Add class labels for cluster 3 divisions
    g['Kelas Hasil'] = '7G'
    h['Kelas Hasil'] = '7H'

    # Save the divided clusters to a single CSV file
    output_data = pd.concat([a, b, c, d, e, f, g, h], axis=0)
    
    # Append 'Kelas Hasil' column to the original data
    data['Kelas Hasil'] = output_data['Kelas Hasil']
    data['Cluster'] = output_data['Cluster']
    
    for _, row in data.iterrows():
        query = "INSERT INTO cluster (nama, peng_sem_1, peng_sem_2, ket_sem_1, ket_sem_2, cluster, kelas_awal ,kelas_akhir) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            str(row['Nama']),
            float(row['Peng Sem 1']),
            float(row['Peng Sem 2']),
            float(row['Ket Sem 1']),
            float(row['Ket Sem 2']),
            str(row['Cluster']),
            str(row['Kelas Hasil']),
            str(row['Kelas Awal'])
        )
        cursor = mysql.connection.cursor()
        cursor.execute(query, values)
        mysql.connection.commit()


@app.route('/clustering', methods=['GET'])
def clusteringKelas():
    return render_template('clusteringkelas.html')

@app.route('/fetch_data-clustering', methods=['GET'])
def fetch_data_clustering():
     # Retrieve data from the database
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM cluster"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()

    # Convert the data into a list of dictionaries
    data_list = []
    for row in data:
        data_dict = {
            'nama': row[1],
            'cluster': row[6],
            'kelas_awal': row[8],
            'kelas_akhir': row[7]
        }
        data_list.append(data_dict)
    return jsonify(data_list)

@app.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    try:
        # Fetch the data using the '/fetch_data-clustering' route
        response = app.test_client().get('/fetch_data-clustering')
        data = response.get_json()

        # Create a custom PDF class that extends FPDF and includes the HTMLMixin
        class PDF(FPDF, HTMLMixin):
            pass

        # Create a new PDF document
        pdf = PDF()

        # Generate the content of the PDF
        pdf.add_page()

        # Set the font style and size
        pdf.set_font('Arial', '', 12)

        # Create the table headers
        table_headers = ['No', 'Nama', 'Cluster', 'Kelas Awal', 'Kelas Hasil']
        table_data = []
        for i, row in enumerate(data):
            row_data = [
                str(i + 1),
                html.escape(row['nama']),
                html.escape(row['cluster']),
                html.escape(row['kelas_awal']),
                html.escape(row['kelas_akhir'])
            ]
            table_data.append(row_data)

        # Write the HTML table structure to the PDF
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.write_html(render_template('table_template.html', table_headers=table_headers, table_data=table_data))

        # Create a response with PDF as attachment
        response = make_response(pdf.output())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=generated_pdf.pdf'

        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_csv')
def generate_csv():
    # Fetch the data using the '/fetch_data-clustering' route
    response = app.test_client().get('/fetch_data-clustering')
    data = response.get_json()
    # Rearrange the keys order in the response data
    reordered_data = [{key: item[key] for key in ['nama', 'cluster', 'kelas_awal', 'kelas_akhir']} for item in data]
    # Create a response object with CSV content type
    response = make_response('')
    response.headers['Content-Disposition'] = 'attachment; filename=generated_data.csv'
    response.headers['Content-Type'] = 'text/csv'

    # Create an in-memory file-like object
    csv_data = io.StringIO()

    # Define the CSV header
    header = ['nama', 'cluster', 'kelas_awal', 'kelas_akhir']

    # Create a CSV writer and write the header to the in-memory file-like object
    writer = csv.DictWriter(csv_data, fieldnames=header)
    writer.writeheader()

    # Write the data to the in-memory file-like object
    writer.writerows(reordered_data)

    # Set the value of the response to the contents of the in-memory file-like object
    response.data = csv_data.getvalue()

    return response 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)