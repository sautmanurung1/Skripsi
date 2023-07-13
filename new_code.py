import random
import numpy as np

# Import the necessary libraries for Flask
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import csv

app = Flask(__name__)

UPLOAD_FOLDER = 'path/to/upload/folder'
ALLOWED_EXTENSIONS = {'csv'}

# Set the upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def k_medoids(X, k, max_iteration=100):
    # Inisialisasi medoids secara acak
    medoids = random.sample(range(len(X)),k)
    
    # Lakukan klasterisasi awal
    clusters = assign_clusters(X, medoids)
    
    # Hitung total simpangan awal
    S = calculate_s(clusters, medoids)
    
    # Lakukan iterasi hingga konvergen atau mencapai batas iterasi maksimum 
    for i in range(max_iteration):
        # Lakukan reposisi medoid
        new_medoids = relocate_medoids(X, clusters)
        
        # Lakukan klasterisasi ulang
        new_clusters = assign_clusters(X, new_medoids)
        
        # Jika total simpangan baru lebih baik, gunakan medoid baru
        new_S = calculate_s(new_clusters, new_medoids)
        if new_S < S:
            medoids = new_medoids
            clusters = new_clusters
            S = new_S
    
    return clusters

def assign_clusters(X, medoids):
    clusters =[[] for _ in range(len(medoids))]
    for i, x in enumerate(X):
        distances = [np.linalg.norm(x - X[m]) for m in medoids]
        cluster_index = np.argmin(distances)
        clusters[cluster_index].append(i)

    return clusters

def calculate_s(clusters, medoids):
    S = 0
    for i, c in enumerate(clusters):
        for j in c:
            S += np.linalg.norm(X[j] - X[medoids[i]])
    return S

def relocate_medoids(X, clusters):
    medoids = []
    for c in clusters:
        distances = [np.sum([np.linalg.norm(X[i] - X[j]) for j in c]) for i in c]
        medoid_index = np.argmin(distances)
        medoids.append(c[medoid_index])
    return medoids

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
            data_list = []
            for row in csv_reader:
                data_list.append({
                    'nama': row['nama'],
                    'pengetahuan1': float(row['pengetahuan semester 1']),
                    'keterampilan1': float(row['keterampilan semester 1']),
                    'pengetahuan2': float(row['pengetahuan semester 2']),
                    'keterampilan2': float(row['keterampilan semester 2'])
                })

        # Convert data_list to a numpy array
        X = np.array([
            [data['pengetahuan1'], data['keterampilan1'], data['pengetahuan2'], data['keterampilan2']]
            for data in data_list
        ])

        # Call the k_medoids function
        k = 3  # Specify the desired number of clusters
        max_iteration = 100  # Specify the maximum number of iterations
        clusters = k_medoids(X, k, max_iteration)

        # Do something with the clusters (e.g., store in the database)

        resp = jsonify({'message': 'File successfully uploaded and data unmarshalled into the database'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are csv'})
        resp.status_code = 400
        return resp

if __name__ == '__main__':
    app.run()
