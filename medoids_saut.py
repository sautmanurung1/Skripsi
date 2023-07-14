import random
import numpy as np

def k_medoids(X, k, max_iterations=100):
    # Inisialisasi medoids secara acak
    medoids = random.sample(range(len(X)), k)

    # Lakukan klasterisasi awal
    clusters = assign_clusters(X, medoids)

    # Hitung total simpangan awal
    S = calculate_s(clusters, medoids)

    # Lakukan iterasi hingga konvergen atau mencapai batas iterasi maksimum
    for i in range(max_iterations):
        # Lakukan reposisi medoid
        new_medoids = relocate_medoids(X, clusters)

        # Lakukan klasterisasi ulang
        new_clusters = assign_clusters(X, new_medoids)

        # Hitung total simpangan baru
        new_S = calculate_s(new_clusters, new_medoids)

        # Jika total simpangan baru lebih baik, gunakan medoid baru
        if new_S < S:
            medoids = new_medoids
            clusters = new_clusters
            S = new_S

    return clusters

def assign_clusters(X, medoids):
    clusters = [[] for _ in range(len(medoids))]
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