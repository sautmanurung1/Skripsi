<?php
/**
 Menghitung jarak kedua node, pake euclidean
*/
function calculateDistance(array $point1, array $point2): float
{
    $x1 = $point1[1];
    $y1 = $point1[2];
    $x2 = $point2[1];
    $y2 = $point2[2];

    //MANHATTAN
    // return abs($x1 - $x2)+abs($y1 - $y2);	    
    // Euclidean distance: sqrt((x2 - x1)^2 + (y2 - y1)^2)
    return sqrt(pow($x2 - $x1, 2) + pow($y2 - $y1, 2));
    
}

/**
 * Fungsi eksekusi algoritma medoid
 */
function medoidAlgorithm(array $dataset, array $medoids, int $maxIterations = 100): array
{
    //menghitung jumlah dataset dan jumlah initial centroid	
    $n = count($dataset);
    $k = count($medoids);
    $clusterAssignments = array_fill(0, $n, 0); // Initialize all data points to cluster 0

    for ($iteration = 0; $iteration < $maxIterations; $iteration++) {
        $clusters = array_fill(0, $k, []);

        // Assign data points to the nearest medoid
        for ($i = 0; $i < $n; $i++) {
            $point = $dataset[$i];
            $minDistance = PHP_INT_MAX;
            $minMedoidIndex = -1;

            for ($j = 0; $j < $k; $j++) {
                $medoid = $medoids[$j];
                $distance = calculateDistance($point, $medoid);
                echo "<pre>";
                echo $distance;
                echo "</pre>";
                if ($distance < $minDistance) {
                    $minDistance = $distance;
                    $minMedoidIndex = $j;
                }
            }

            $clusterAssignments[$i] = $minMedoidIndex;
            $clusters[$minMedoidIndex][] = $i;
        }
        // Update medoids
        $newMedoids = [];

        for ($j = 0; $j < $k; $j++) {
            $clusterIndices = $clusters[$j];
            $minCost = PHP_INT_MAX;
            $minCostIndex = -1;

            foreach ($clusterIndices as $clusterIndex) {
                $cost = 0;
                foreach ($clusterIndices as $otherIndex) {
                    $otherPoint = $dataset[$otherIndex];
                    $cost += calculateDistance($dataset[$clusterIndex], $otherPoint);
                }
                /*
                  jika cost baru lebih kecil, maka centroid baru menggunakan
                */
                if ($cost < $minCost) {
                    $minCost = $cost;
                    $minCostIndex = $clusterIndex;
                }
            }
            $newMedoids[$j] = $dataset[$minCostIndex];
        }
        // If medoids are not updated, terminate the algorithm
        if ($medoids === $newMedoids) {
            break;
        }

        $medoids = $newMedoids;
    }

    return ['clusterAssignments' => $clusterAssignments, 'medoids' => $medoids];
}

// Usage example:
$dataset = [
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
];
$initialMedoids = [
    ['C1', 3, 4],
    ['C2', 7, 4],
];
$maxIterations = 100;
echo "---";
$result = medoidAlgorithm($dataset, $initialMedoids, $maxIterations);
$clusterAssignments = $result['clusterAssignments'];
$medoids = $result['medoids'];

// Display the cluster assignments and medoids
echo "<pre>";
echo "Datasets:\n";
print_r($dataset);
echo "Init Medoid:\n";
print_r($initialMedoids);
echo "Cluster Assignments:\n";
print_r($clusterAssignments);
echo "Medoids:\n";
print_r($medoids);
echo "</pre>";
?>
