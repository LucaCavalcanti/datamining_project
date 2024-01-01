import sys
sys.path.append('feature_extraction')
from feature_extraction import feature_extraction as fe

import ijson
import numpy as np

from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

from sklearn.cluster import AgglomerativeClustering

from copy import deepcopy

# WARNING: these are placeholder values
SAMPLE_BUFFER_SIZE = 50                 # ideally, the buffer should be as large as possible, a bit larger than the actual buffer as retainedset/compressedsets are not present in the sampling phase
BUFFER_SIZE = 10                        # ideally, the buffer should be as large as possible
MAHALANOBIS_DISTANCE_THRESHOLD = 30

Clusters = []       # the primary clusters
RetainedSet = []    # the array of routes that did not fit any cluster
Miniclusters = []   # the clusters created with the RetainedSet
CompressedSets = [] # the secondary clusters created with the Miniclusters and older CompressedSets
Buffer = []
mahalanobis_distances = []
number_of_clusters = 0
number_of_compressed_sets = 0
actual_routes_stream = None

class Cluster:
    def __init__(self, standard_route, index):
        self.centroid = standard_route
        self.size = 1
        self.index = index
        self.mahalanobis_threshold = 0

        # servono?
        self.sum = []
        self.sum_squares = []
        self.routes = []
    
    def __str__(self):
        return f"Cluster: {self.index}\nCentroid: {self.centroid}\nSize: {self.size}"

    def add(self, route):
        self.size += 1
        self.routes.append(route)
    
    def update_centroid(self):
        # find the new centroid by taking the route with the minimum distance from all the other routes in the cluster
        self.routes.append(self.centroid)
        min_distance = sys.maxsize
        min_route = None
        city_indexes, cities_res, merch_indexes, merch_res = fe.get_features_total(self.routes)
        route_counter = 0
        other_route_counter = 0
        for route in self.routes:
            distance = 0
            for other_route_counter in range(len(self.routes)):
                distance += custom_distance(cities_res[route_counter], cities_res[other_route_counter], merch_res[route_counter], merch_res[other_route_counter])
            # TODO: do we need to divide by the number of routes?
            if distance < min_distance:
                min_distance = distance
                min_route = route
            route_counter += 1
        self.centroid = min_route
        self.routes = [] 
        print("New centroid for cluster", self.index, "is", self.centroid["id"])


def BFR(standard_routes, actual_routes):
    # INITIALIZATION STEP
    # Set the number of clusters to the number of standard routes, set the cluster centroids to the standard routes
    init_clusters(standard_routes)
    sample_actual_routes(actual_routes)
    find_mahalanobis_thresholds()
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
    print("Compressed Sets:")
    for compressedset in CompressedSets:
        print(compressedset)
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

def sample_actual_routes(actual_routes):
    global Buffer
    Buffer = []

    counter = 0
    # get number of actual routes    
    with open(actual_routes, "rb") as f:
        for route in ijson.items(f, "item"):
            counter += 1
    
    # get a sample of actual routes
    sample_indexes = np.random.choice(counter, SAMPLE_BUFFER_SIZE, replace=False)
    print("Sample indexes:", sample_indexes)

    # get the actual routes at the sample indexes
    id_counter = 0
    with open(actual_routes, "rb") as f:
        for route in ijson.items(f, "item"):
            if id_counter in sample_indexes:
                Buffer.append(route)
            id_counter += 1

def find_mahalanobis_thresholds():
    global Buffer, mahalanobis_distances
    mahalanobis_distances = np.zeros((len(Clusters), len(Buffer)))

    # using the sample buffer, calculate the Mahalanobis distance between each route and the centroid of each cluster
    # then, calculate the average distance between each route and the centroid of its cluster   
    # finally, calculate the average of all the average distances
    # this value will be used as the Mahalanobis distance threshold
    route_counter = 0
    for route in Buffer:
        for cluster in Clusters:
            mahalanobis_distances[cluster.index][route_counter] = mahalanobis_distance(route, cluster.centroid)
        route_counter += 1
    
    for cluster in Clusters:
        cluster_distances = mahalanobis_distances[cluster.index]
        cluster_distances = cluster_distances[cluster_distances != 0]
        cluster.mahalanobis_threshold = np.average(cluster_distances)
        print("Mahalanobis threshold for cluster", cluster.index, "is", cluster.mahalanobis_threshold)

    Buffer.clear()

    

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
    for cluster in Clusters:
        cluster.update_centroid()

def primary_compression_criteria():
    global Buffer, Clusters, RetainedSet
    for route in Buffer:
        
        # Find closest cluster to route by passing all of them 
        closest_cluster, closest_distance = find_closest_cluster(route)    
        # If closest cluster is under a certain distance threshold:
        if closest_distance < Clusters[closest_cluster].mahalanobis_threshold:
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
    # k = int(number_of_clusters * 0.3 + number_of_clusters)
    k = 10 #TODO: REMOVE THIS PLAECHOLDER

    # idea: we need at least two routes per cluster to have some kind of results
    min_number_of_routes_to_cluster = 2*k
    if len(RetainedSet) >= min_number_of_routes_to_cluster:
        # cluster the retained set with K-Means
        print("Clustering retained set with K-Means")
        retainedSet_cluster_labels = cluster_retained_set(k)
        # add the new clusters to the set of compressed sets
        add_miniclusters_to_compressed_sets(retainedSet_cluster_labels)

    for cluster in CompressedSets:
        cluster.update_centroid()

    # min_number_of_routes_to_cluster_compressedsets = 2 * number_of_clusters
    min_number_of_routes_to_cluster_compressedsets = 5 #TODO: REMOVE THIS PLAECHOLDER

    if number_of_compressed_sets >= min_number_of_routes_to_cluster_compressedsets:
        # cluster the compressed sets with Hierarchical clustering
        print("Clustering compressed sets with Hierarchical clustering")

        # cluster_compressed_sets(number_of_clusters)
        cluster_compressed_sets(5) #TODO: REMOVE THIS PLAECHOLDER

    for cluster in CompressedSets:
        cluster.update_centroid()
    
def cluster_retained_set(k):
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
    kmeans = KMeans(n_clusters=k, init='k-means++', algorithm='lloyd', n_init=10)
    kmeans.fit(distance_matrix)

    # Get cluster labels -> [0, 1, 1, 0] means route 0 has cluster index 0, route 1 has cluster index 1, etc.
    labels = kmeans.labels_
    print("Cluster labels:", labels)

    return labels

def custom_distance(cities_A, cities_B, merch_A, merch_B):
    # this function should, given the vectorial representation of routes A and B, parse their distance and return its value.
    return 1

def add_miniclusters_to_compressed_sets(labels):
    global RetainedSet, CompressedSets, number_of_compressed_sets

    # Count how many routes are in each cluster
    clusters_count = {}
    labels_len = len(labels)
    for i in range(labels_len):
        if labels[i] in clusters_count:
            # K-Means cluster label was already considered, add route to respective CompressedSet and remove it from the RetainedSet
            clusters_count[labels[i]] += 1
        else:
            # K-Means cluster label wasn't already considered, create new cluster to add to CompressedSet (can't remove route from RetainedSet, cluster might have size 1)
            clusters_count[labels[i]] = 1

    new_retainedSet = []

    indexes = {}
    for i in range(labels_len):
        if clusters_count[labels[i]] > 1:
            if labels[i] in indexes:
                CompressedSets[indexes[labels[i]]].add(RetainedSet[i])
            else:
                indexes[labels[i]] = number_of_compressed_sets
                CompressedSets.append(Cluster(RetainedSet[i], number_of_compressed_sets))
                number_of_compressed_sets += 1
            print("Adding route", RetainedSet[i]["id"], "to compressed set", indexes[labels[i]])
        else:
            new_retainedSet.append(RetainedSet[i])
            print("Adding route", RetainedSet[i]["id"], "to new retained set")
    
    RetainedSet = new_retainedSet
            
def cluster_compressed_sets(k):
    global CompressedSets
    distance_matrix = np.zeros((len(CompressedSets), len(CompressedSets)))

    compressedSets_centroids = []
    for cluster in CompressedSets:
        compressedSets_centroids.append(cluster.centroid)

    city_indexes, cities_res, merch_indexes, merch_res = fe.get_features_total(compressedSets_centroids)
    for i in range(len(CompressedSets)):
        # pick all routes from the next one to the end
        for j in range(i + 1, len(CompressedSets)):
            distance_matrix[i][j] = custom_distance(cities_res[i], cities_res[j], merch_res[i], merch_res[j])
    # make the distance matrix symmetric
    distance_matrix = distance_matrix + distance_matrix.T

    # Perform hierarchical clustering
    clustering = AgglomerativeClustering(n_clusters=k, metric='precomputed', linkage='average')
    cluster_labels = clustering.fit_predict(distance_matrix)

    update_CompressedSets(cluster_labels)

def update_CompressedSets(labels):
    global CompressedSets, number_of_compressed_sets

    new_number_of_compressed_sets = 0

    new_compressedSets = []

    labels_len = len(labels)
    indexes = {}
    for i in range(labels_len):
        if labels[i] in indexes:
            new_compressedSets[indexes[labels[i]]].add(CompressedSets[i].centroid)
            new_compressedSets[indexes[labels[i]]].size += CompressedSets[i].size - 1
        else:
            indexes[labels[i]] = new_number_of_compressed_sets
            new_compressedSets.append(Cluster(CompressedSets[i].centroid, new_number_of_compressed_sets))
            new_compressedSets[indexes[labels[i]]].size += CompressedSets[i].size - 1
            new_number_of_compressed_sets += 1
        print("Adding old cluster centroid", CompressedSets[i].centroid["id"], "to compressed set", indexes[labels[i]])
    
    number_of_compressed_sets = new_number_of_compressed_sets
    CompressedSets = new_compressedSets

if __name__ == "__main__":
    BFR("data/small/standard_small.json", "data/small/actual_normal_small.json")