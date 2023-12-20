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

# Set initial cluster centroids to the standard routes
def init_clusters(standard_routes):
    global number_of_clusters
    number_of_clusters = 0
    with open(standard_routes, "rb") as f:
        for route in ijson.items(f, "item"):
            Clusters.append(Cluster(route, number_of_clusters))
            number_of_clusters += 1

# Open actual routes JSON file
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

                # Buffer has been read completely, use it
                stream_buffer()
                Buffer.clear()
        
        if len(Buffer) != 0:
            # Buffer is not empty, use it
            stream_buffer()
            Buffer.clear()

    except ijson.common.IncompleteJSONError:
        print("IncompleteJSONError")

# For each route in the buffer, check:
# - primary compression criteria: can we add the route directly in a cluster? (This is done by looking at the Mahalanobis distance)
# - secondary compression criteria: all routes that are not added to clusters go to the RetainedSet. Cluster it with K-Means and then 
#                                   compare these clusters with the CompressedSet. If needed and if possible, cluster the two sets 
#                                   using Hierarchical clustering
def stream_buffer():
    global Buffer, Clusters, RetainedSet
    primary_compression_criteria()
    secondary_compression_criteria()

def primary_compression_criteria():
    global Buffer, Clusters, RetainedSet
    for route in Buffer:
        
        # Find closest cluster to route by passing all of them 
        closest_cluster, closest_distance = find_closest_cluster(route)    
        # If closest cluster is under a certain distance threshold:
        if closest_distance < MAHALANOBIS_DISTANCE_THRESHOLD:
            # add the route to the cluster
            print("Adding route", route["id"], "to cluster", closest_cluster)
            Clusters[closest_cluster].add(route)
        else:
            # add the route to the retained set
            print("Adding route", route["id"], "to retained set")
            RetainedSet.append(route)

        # remove the route from the buffer
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

# Cluster with K-Means the RetainedSet. We set k to be 30% more than the actual number of clusters in the Clusters[] array (the paper says to do so)
def secondary_compression_criteria():
    global RetainedSet, CompressedSets
    k = int(number_of_clusters * 0.3 + number_of_clusters)

    # idea: we need at least two routes per cluster to have some kind of results
    min_number_of_routes_to_cluster = 2*k
    if len(RetainedSet) >= min_number_of_routes_to_cluster:
        # cluster the retained set with K-Means
        print("Clustering retained set with K-Means")
        retainedSet_cluster_labels = cluster_retained_set(k)
        # add the new clusters to the set of compressed sets
        add_miniclusters_to_compressed_sets(retainedSet_cluster_labels)

        # TODO: if the compressed sets are large enough, merge them with Hierarchical clustering

def cluster_retained_set(k):
    # In order
    global RetainedSet, CompressedSets
    distance_matrix = np.zeros((len(RetainedSet), len(RetainedSet)))
    city_indexes, cities_res, merch_indexes, merch_res = fe.get_features_total(RetainedSet)
    for i in range(len(RetainedSet)):
        # pick all routes from the next one to the end
        for j in range(i + 1, len(RetainedSet)):
            distance_matrix[i][j] = custom_distance(cities_res[i], cities_res[j], merch_res[i], merch_res[j])
    # make the distance matrix symmetric
    distance_matrix = distance_matrix + distance_matrix.T

    # Perform K-Means clustering with the custom distance metric
    kmeans = KMeans(n_clusters=k, init='k-means++', algorithm='full')
    kmeans.fit(distance_matrix)

    # Get cluster labels -> [0, 1, 1, 0] means route 0 has cluster index 0, route 1 has cluster index 1, etc.
    labels = kmeans.labels_
    print("Cluster labels:", labels)

    # TODO: create miniclusters from the labels

    return labels

def custom_distance(cities_A, cities_B, merch_A, merch_B):
    # this function should, given the vectorial representation of routes A and B, parse their distance and return its value.
    return 1

def add_miniclusters_to_compressed_sets(labels):
    global RetainedSet, CompressedSets
    # Count how many routes are in each cluster
    clusters_count = {}
    for i in range(len(labels)):
        if labels[i] in clusters_count:
            clusters_count[labels[i]] += 1
        else:
            clusters_count[labels[i]] = 1
    
    # TODO: Add the clusters to the Compressed Sets if they have at least 2 routes



if __name__ == "__main__":
    BFR("data/small/standard_small.json", "data/small/actual_normal_small.json")