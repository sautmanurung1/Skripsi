import math

def calculate_distance(point1, point2):
    x1, y1 = point1[1], point1[2]
    x2, y2 = point2[1], point2[2]

    # Manhattan distance: abs(x1 - x2) + abs(y1 - y2)
    # return abs(x1 - x2) + abs(y1 - y2)

    # Euclidean distance: sqrt((x2 - x1)^2 + (y2 - y1)^2)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def medoid_algorithm(dataset, medoids, max_iterations=100):
    n = len(dataset)
    k = len(medoids)
    cluster_assignments = [0] * n

    for iteration in range(max_iterations):
        clusters = [[] for _ in range(k)]

        for i in range(n):
            point = dataset[i]
            min_distance = float('inf')
            min_medoid_index = -1

            for j in range(k):
                medoid = medoids[j]
                distance = calculate_distance(point, medoid)

                if distance < min_distance:
                    min_distance = distance
                    min_medoid_index = j

            cluster_assignments[i] = min_medoid_index
            clusters[min_medoid_index].append(i)

        new_medoids = []

        for j in range(k):
            cluster_indices = clusters[j]
            min_cost = float('inf')
            min_cost_index = -1

            for cluster_index in cluster_indices:
                cost = 0

                for other_index in cluster_indices:
                    other_point = dataset[other_index]
                    cost += calculate_distance(dataset[cluster_index], other_point)

                if cost < min_cost:
                    min_cost = cost
                    min_cost_index = cluster_index

            new_medoids.append(dataset[min_cost_index])

        if medoids == new_medoids:
            break

        medoids = new_medoids

    return {'cluster_assignments': cluster_assignments, 'medoids': medoids}

# Usage example:
dataset = [
    ['X1', 2, 6],
    ['X2', 3, 4],
    ['X3', 3, 8],
    ['X4', 4, 7],
    ['X5', 6, 2],
    ['X6', 6, 4],
    ['X7', 7, 3],
    ['X8', 7, 4],
    ['X9', 8, 5],
    ['X10', 7, 6]
]
initial_medoids = [
    ['C1', 3, 4],
    ['C2', 7, 4],
]
max_iterations = 100
print("---")
result = medoid_algorithm(dataset, initial_medoids, max_iterations)
cluster_assignments = result['cluster_assignments']
medoids = result['medoids']

# Display the cluster assignments and medoids
print("Datasets:")
print(dataset)
print("Init Medoid:")
print(initial_medoids)
print("Cluster Assignments:")
print(cluster_assignments)
print("Medoids:")
print(medoids)
