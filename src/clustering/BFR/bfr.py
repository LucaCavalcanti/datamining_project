import sys
sys.path.append('feature_extraction')
from feature_extraction import feature_extraction as fe

import ijson
import numpy as np

BUFFER_SIZE = 2
MAHALANOBIS_DISTANCE_THRESHOLD = 50

Clusters = []
RetainedSet = []
CompressedSets = []
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

    # city_indexes, cities_A, cities_B, merch_indexes, merch_A, merch_B = fe.get_features(fe.route_example, fe.route_example)
    # print(city_indexes)
    # print(cities_A)
    # print(cities_B)
    # print()
    # print(merch_indexes)
    # print(merch_A)
    # print(merch_B)

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
    for route in Buffer:
        closest_cluster, closest_distance = find_closest_cluster(route)    
        if closest_distance < MAHALANOBIS_DISTANCE_THRESHOLD:
            # add the route to the cluster
            print("Adding route to cluster")
            Clusters[closest_cluster].add(route)    
        else:
            # add the route to the retained set
            print("Adding route to retained set")
            RetainedSet.append(route)
    

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
    return np.random.randint(0, 100)

if __name__ == "__main__":
    BFR("data/standard.json", "data/actual_normal.json")