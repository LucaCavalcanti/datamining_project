import sys
sys.path.append('feature_extraction')
from feature_extraction import feature_extraction as fe

import ijson
import numpy as np

from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

# WARNING: these are placeholder values
BUFFER_SIZE = 10
MAHALANOBIS_DISTANCE_THRESHOLD = 30

Clusters = []       # the primary clusters
RetainedSet = []    # the array of routes that did not fit any cluster
CompressedSets = [] # the secondary clusters created with the Miniclusters and older CompressedSets
Miniclusters = []   # the clusters created with the RetainedSet
Buffer = []
number_of_clusters = 0
actual_routes_stream = None

class Cluster:
    def __init__(self, standard_route, index):
        self.centroid = standard_route
        self.size = 1
        self.index = index

        # servono?
        self.sum = []
        self.sum_squares = []
    
    def __str__(self):
        return f"Cluster: {self.index}\nCentroid: {self.centroid}\nSize: {self.size}"

    def add(self, route):
        self.size += 1
        self.update_centroid(route)
    
    def update_centroid(self, route):
        # TODO: how do we update a cluster's centroid?
        pass

def BFR(standard_routes, actual_routes):
    # INITIALIZATION STEP
    # Set the number of clusters to the number of standard routes, set the cluster centroids to the standard routes
    init_clusters(standard_routes)
    init_actual_routes_stream(actual_routes)

    # REPEAT
    #     Fill buffer with X actual routes
    #     For each route in the buffer
    #         Find the closest cluster centroid
    #         If the route is close enough to the centroid
    #             Add the route to the cluster
    #         Else
    #             Add the route to the Retained Set
    #     Adjust the cluster centroids
    #     If the Retained Set is large enough
    #         Cluster the Retained Set with K-Means
    #         Add the new clusters to the set of Compressed Sets
    #     If the Compressed Sets are large enough
    #         Merge the Compressed Sets with Hierarchical clustering
    # UNTIL the buffer is empty
    # Merge each Compressed Set to the nearest cluster

    keep_filling_buffer()

    print("Clusters:")
    for cluster in Clusters:
        print(cluster)
        print()
    print("Retained Set:")
    for route in RetainedSet:
        print(route)
        print()
    # do something with the final results

def init_clusters(standard_routes):
    global number_of_clusters
    number_of_clusters = 0
    with open(standard_routes, "rb") as f:
        for route in ijson.items(f, "item"):
            Clusters.append(Cluster(route, number_of_clusters))
            number_of_clusters += 1

def init_actual_routes_stream(actual_routes):
    global actual_routes_stream
    actual_routes_stream = open(actual_routes, "rb")


# Keep filling the buffer until the actual_routes file is read in its entirety
def keep_filling_buffer():
    global Buffer
    Buffer = []
    try:
        # Parse all the actual routes
        for route in ijson.items(actual_routes_stream, "item"):
            Buffer.append(route)
            if len(Buffer) == BUFFER_SIZE:

                # do something with the buffer
                stream_buffer()
                Buffer.clear()
        
        if len(Buffer) != 0:
            # Buffer is not empty, use it
            stream_buffer()
            Buffer.clear()

    except ijson.common.IncompleteJSONError:
        print("IncompleteJSONError")

def stream_buffer():
    global Buffer, Clusters, RetainedSet
    primary_compression_criteria()
    secondary_compression_criteria()

def primary_compression_criteria():
    global Buffer, Clusters, RetainedSet
    for route in Buffer:
        closest_cluster, closest_distance = find_closest_cluster(route)    
        if closest_distance < MAHALANOBIS_DISTANCE_THRESHOLD:
            # add the route to the cluster
            print("Adding route", route["id"], "to cluster", closest_cluster)
            Clusters[closest_cluster].add(route)
            # remove the route from the buffer
            Buffer = [r for r in Buffer if r != route]
        else:
            # add the route to the retained set
            print("Adding route", route["id"], "to retained set")
            RetainedSet.append(route)
            Buffer = [r for r in Buffer if r != route]

def find_closest_cluster(route):
    closest_cluster = None
    closest_distance = sys.maxsize
    for cluster in Clusters:
        distance = mahalanobis_distance(route, cluster.centroid)
        if distance < closest_distance:
            closest_cluster = cluster.index
            closest_distance = distance
    
    return closest_cluster, closest_distance


def mahalanobis_distance(route, centroid):
    # TODO: how do we calculate the distance between a route and a centroid?
    return 50

def secondary_compression_criteria():
    global RetainedSet, CompressedSets
    k = int(number_of_clusters * 0.3 + number_of_clusters)
    if len(RetainedSet) >= k:
        # cluster the retained set with K-Means
        print("Clustering retained set with K-Means")
        cluster_retained_set()

def cluster_retained_set():
    global RetainedSet, CompressedSets
    distance_matrix = np.zeros((len(RetainedSet), len(RetainedSet)))
    city_indexes, cities_res, merch_indexes, merch_res = fe.get_features_total(RetainedSet)
    for i in range(len(RetainedSet)):
        # pick all routes from the next one to the end
        for j in range(i + 1, len(RetainedSet)):
            distance_matrix[i][j] = custom_distance(cities_res[i], cities_res[j], merch_res[i], merch_res[j])
    # make the distance matrix symmetric
    distance_matrix = distance_matrix + distance_matrix.T
    

def custom_distance(cities_A, cities_B, merch_A, merch_B):
    # this function should, given the vectorial representation of routes A and B, parse their distance and return its value.
    return 1


if __name__ == "__main__":
    BFR("data/small/standard_small.json", "data/small/actual_normal_small.json")