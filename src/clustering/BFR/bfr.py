import sys
sys.path.append('src/clustering/BFR/feature_extraction')
from feature_extractions import get_features, get_features_total
from similarity import similarity

import ijson
import json
import numpy as np

from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.exceptions import ConvergenceWarning

from time import time
# import concurrent.futures
import os

# WARNING: these are placeholder values
SAMPLE_BUFFER_SIZE = 500                 # ideally, the buffer should be as large as possible, a bit larger than the actual buffer as retainedset/compressedsets are not present in the sampling phase
BUFFER_SIZE = 200                        # ideally, the buffer should be as large as possible

CITY_WEIGHTS = 0.5
MERCH_WEIGHTS = 0.5

max_threads = min(32, (os.cpu_count() or 1) + 4)

Clusters = []       # the primary clusters
RetainedSet = []    # the array of routes that did not fit any cluster
Miniclusters = []   # the clusters created with the RetainedSet
CompressedSets = [] # the secondary clusters created with the Miniclusters and older CompressedSets
Buffer = []
number_of_clusters = 0
number_of_compressed_sets = 0
actual_routes_stream = None

time_start = None
time_temp = None
mahalanobis_distances_times = []
custom_distances_times = []
centroid_update_times = []
primary_compression_criteria_times = []
secondary_compression_criteria_times = []
stream_buffer_times = []
cluster_retained_set_times = []
add_miniclusters_to_compressed_sets_times = []
cluster_compressed_sets_times = []

update_CompressedSets_times = []


class Cluster:
    def __init__(self, standard_route, index):
        self.centroid = standard_route
        self.size = 1
        self.size_before_centroid_update = 1
        self.index = index
        self.mahalanobis_threshold = 0

        self.routes = []
        self.routesweights = {}
        self.original_sroute_id = standard_route["id"]
    
    def __str__(self):
        return f"Cluster: {self.index}\nCentroid: {self.centroid}\nSize: {self.size}"

    def add(self, route, centorid_weight=1):
        self.size += 1
        self.routes.append(route)
        self.routesweights[route["id"]] = centorid_weight
    
    def update_centroid(self):
        # find the new centroid by taking the route with the minimum distance from all the other routes in the cluster
        if len(self.routes) > 2:
            time_temp = time()
            print(get_elapsed_time(), ":     Updating centroid for cluster", self.index, "with size", self.size)
            self.routes.append(self.centroid)
            self.routesweights[self.centroid["id"]] = self.size_before_centroid_update
            min_distance = sys.maxsize
            min_route = None
            city_indexes, cities_res, merch_indexes, merch_res = get_features_total(self.routes)
            route_counter = 0
            for route in self.routes:
                # print(get_elapsed_time(), ":        -----")
                distance = 0

                distances = []
                # def compute_distances(thread_routes, distances, route_counter):
                #     # print(get_elapsed_time(), ":        Calculating distances for new centroids with threads. Thread size:", len(thread_routes))
                #     for other_route_counter in range(len(thread_routes)):
                #         if route_counter == other_route_counter:
                #             continue
                #         distance_temp = custom_distance(city_indexes, cities_res[route_counter], cities_res[other_route_counter], merch_indexes, merch_res[route_counter], merch_res[other_route_counter])
                #         weight = self.routesweights[self.routes[route_counter]["id"]] / (self.routesweights[thread_routes[other_route_counter]["id"]] + self.routesweights[self.routes[route_counter]["id"]] )
                #         distance_temp = weight * distance_temp
                #         distances.append(distance_temp)

                # with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                #     # Split the routes list into chunks for each thread
                #     chunks = [self.routes[i:i + 5] for i in range(0, len(self.routes), 5)]
                #     futures = {executor.submit(compute_distances, chunk, distances, route_counter): chunk for chunk in chunks}

                for other_route_counter in range(len(self.routes)):
                    # print("Checking route", route["id"], "with route", self.routes[other_route_counter]["id"])
                    if route_counter == other_route_counter:
                        continue
                    distance_temp = custom_distance(city_indexes, cities_res[route_counter], cities_res[other_route_counter], merch_indexes, merch_res[route_counter], merch_res[other_route_counter])
                    weight = self.routesweights[self.routes[route_counter]["id"]] / (self.routesweights[self.routes[other_route_counter]["id"]] + self.routesweights[self.routes[route_counter]["id"]] )
                    distance_temp = weight * distance_temp
                    distances.append(distance_temp)
                    # distance += custom_distance(cities_res[route_counter], cities_res[other_route_counter], merch_res[route_counter], merch_res[other_route_counter])
                
                if sum(distances) < min_distance:
                    min_distance = sum(distances)
                    min_route = route
                route_counter += 1


            self.centroid = min_route
            self.routes = [] 
            self.size_before_centroid_update = self.size

            time_temp2 = time()
            centroid_update_times.append(time_temp2 - time_temp)
            print(get_elapsed_time(), ":     New centroid for cluster", self.index, "is", self.centroid["id"], "with size", self.size)

def get_elapsed_time():
    time_now = time()
    # return with two decimals precision
    return round(time_now - time_start, 2)

def print_average_times():
    # average over the times
    print("Average mahalanobis distance time:", np.average(mahalanobis_distances_times))
    print("Average custom distance time:", np.average(custom_distances_times))
    print("Average centroid update time:", np.average(centroid_update_times))
    print("Average primary compression criteria time:", np.average(primary_compression_criteria_times))
    print("Average secondary compression criteria time:", np.average(secondary_compression_criteria_times))
    print("Average stream buffer time:", np.average(stream_buffer_times))
    print("Average cluster retained set time:", np.average(cluster_retained_set_times))
    print("Average add miniclusters to compressed sets time:", np.average(add_miniclusters_to_compressed_sets_times))
    print("Average cluster compressed sets time:", np.average(cluster_compressed_sets_times))
    print("Average update compressed sets time:", np.average(update_CompressedSets_times))

def BFR(standard_routes, actual_routes, results_file):
    global time_start
    # INITIALIZATION STEP
    # Set the number of clusters to the number of standard routes, set the cluster centroids to the standard routes
    time_start = time()
    print(get_elapsed_time(), ": Initializing BFR")
    init_clusters(standard_routes)

    print(get_elapsed_time(), ": Sampling from actual routes")
    sample_actual_routes(actual_routes)
    
    print(get_elapsed_time(), ": Finding route and merch distance weights")
    find_route_and_merch_distance_weights()
    
    print(get_elapsed_time(), ": Finding Mahalanobis thresholds")
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
    print(get_elapsed_time(), ": Starting BFR")
    keep_filling_buffer()

    print(get_elapsed_time(), ": Merging compressed sets with primary clusters")
    merge_compressed_sets_with_primary_clusters()

    print(get_elapsed_time(), ": Writing results to file")
    write_results_to_file(results_file)

    print(get_elapsed_time(), ": BFR has ended!")
    # print("Retained Set:")
    # for route in RetainedSet:
    #     print(route)
    #     print()
    # print("Clusters:")
    # for cluster in Clusters:
    #     print(cluster)
    #     print()
    # print("Compressed Sets:")
    # for compressedset in CompressedSets:
    #     print(compressedset)
    #     print()
    # do something with the final results
    print_average_times()

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
    #print("Sample indexes:", sample_indexes)

    # get the actual routes at the sample indexes
    id_counter = 0
    with open(actual_routes, "rb") as f:
        for route in ijson.items(f, "item"):
            if id_counter in sample_indexes:
                Buffer.append(route)
            id_counter += 1

def find_route_and_merch_distance_weights():
    global CITY_WEIGHTS, MERCH_WEIGHTS
    
    merch_cosines = []
    city_cosines = []

    # by using the Buffer, calculate the distance between each route and the respective centroid (use the actual route's reference standard route to find the centroid)
    for route in Buffer:
        for cluster in Clusters:
            if route["sroute"] == cluster.original_sroute_id:
                # print("Route", route["id"], "with cluster", cluster.index, "has driver", route["driver"])
                city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch = get_features(cluster.centroid, route)
                merch_cosine, city_cosine = similarity(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch)
                merch_cosines.append(merch_cosine)
                city_cosines.append(city_cosine)
                # print("Route", route["id"], "has merch cosine", merch_cosine, "and city cosine", city_cosine, "with cluster", cluster.index)
                break
    
    # calculate averages of merch and city cosine values, these values are between 0 and 1
    avg_merch_cosine = np.average(merch_cosines)
    avg_city_cosine = np.average(city_cosines)

    # set weights to be the inverse of the averages and for them to sum to 1
    CITY_WEIGHTS = avg_merch_cosine / (avg_merch_cosine + avg_city_cosine)
    MERCH_WEIGHTS = avg_city_cosine / (avg_merch_cosine + avg_city_cosine)

    # invert the weights so that the higher the cosine value, the higher the weight
    CITY_WEIGHTS = 1 - CITY_WEIGHTS
    MERCH_WEIGHTS = 1 - MERCH_WEIGHTS

    #print("average merch cosine:", avg_merch_cosine)
    #print("average city cosine:", avg_city_cosine)
    print(get_elapsed_time(), ":     city weights:", CITY_WEIGHTS)
    print(get_elapsed_time(), ":     merch weights:", MERCH_WEIGHTS)
        
def find_mahalanobis_thresholds():
    global Buffer
    mahalanobis_distances = [[] for i in range(number_of_clusters)]

    # using the sample buffer, calculate the Mahalanobis distance between each route and the centroid of each cluster
    # then, calculate the average distance between each route and the centroid of its cluster   
    # finally, calculate the average of all the average distances
    # this value will be used as the Mahalanobis distance threshold
    route_counter = 0
    for route in Buffer:
        for cluster in Clusters:
            # if route["sroute"] == cluster.original_sroute_id:
            mahalanobis_distances[cluster.index].append(mahalanobis_distance(route, cluster.centroid))
        route_counter += 1
    
    for cluster in Clusters:
        cluster_distances = mahalanobis_distances[cluster.index]
        # cluster_distances = cluster_distances[cluster_distances != 0]
        cluster.mahalanobis_threshold = max(0.6, np.average(cluster_distances))
        print(get_elapsed_time(), ":     Mahalanobis threshold for cluster", cluster.index, "is", cluster.mahalanobis_threshold, ", average was", np.average(cluster_distances))

    Buffer.clear()


def mahalanobis_distance(route, centroid):
    time_temp = time()
    city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch = get_features(centroid, route)
    time_temp2 = time()
    mahalanobis_distances_times.append(time_temp2 - time_temp)
    return custom_distance(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch)

def custom_distance(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch):
    # this function should, given the vectorial representation of routes A and B, parse their distance and return its value.
    time_temp = time()
    merch_cosine, city_cosine = similarity(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch)
    time_temp2 = time()
    custom_distances_times.append(time_temp2 - time_temp)
    return CITY_WEIGHTS * (1 - city_cosine) + MERCH_WEIGHTS * (1 - merch_cosine)

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
                print(get_elapsed_time(), ":     Buffer is full")
                stream_buffer()
                Buffer.clear()
        
        if len(Buffer) != 0:
            # Buffer is not empty, use it
            print(get_elapsed_time(), ":     Last cycle, Buffer isn't empty, using it")
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

    time_temp = time()
    print(get_elapsed_time(), ":     Checking primary compression criteria")
    primary_compression_criteria()
    time_temp2 = time()
    primary_compression_criteria_times.append(time_temp2 - time_temp)

    time_temp3 = time()
    print(get_elapsed_time(), ":     Checking secondary compression criteria")
    secondary_compression_criteria()
    time_temp4 = time()
    secondary_compression_criteria_times.append(time_temp4 - time_temp3)

    print(get_elapsed_time(), ":     Updating primary clusters centroids")
    for cluster in Clusters:
        cluster.update_centroid()

    time_temp5 = time()
    stream_buffer_times.append(time_temp5 - time_temp)

def primary_compression_criteria():
    global Buffer, Clusters, RetainedSet
    for route in Buffer:
        # Find closest cluster to route by passing all of them 
        closest_cluster, closest_distance = find_closest_cluster(route)    
        # If closest cluster is under a certain distance threshold:
        # if closest_distance < 0.6:
        if closest_distance < Clusters[closest_cluster].mahalanobis_threshold:
            # add the route to the cluster
            print("         Adding route", route["id"], "to cluster", closest_cluster, "with distance", closest_distance)
            Clusters[closest_cluster].add(route)
        else:
            # add the route to the retained set
            print("         Adding route", route["id"], "to retained set")
            RetainedSet.append(route)

        # remove the route from the buffer
        Buffer = [r for r in Buffer if r != route]

def find_closest_cluster(route):
    closest_cluster = None
    closest_distance = sys.maxsize
    for cluster in Clusters:
        # print("Checking route", route["id"] , "with cluster", cluster.index)
        distance = mahalanobis_distance(route, cluster.centroid)
        if distance < closest_distance:
            closest_cluster = cluster.index
            closest_distance = distance
    
    return closest_cluster, closest_distance

# Cluster with K-Means the RetainedSet, and then the ComrpessedSets with Hierarchical. 
# the RetainedSet will be clustered into k clusters, where k is a percentage of the number of clusters
# the CompressedSets will be clustered into h clusters, where h is a percentage of the number of CompressedSets
# we want h to be smaller than k but larger than the number of primary clusters.
def secondary_compression_criteria():
    global RetainedSet, CompressedSets
    k = int(number_of_clusters * 0.5 + number_of_clusters)


    # idea: we need at least two routes per cluster to have some kind of results
    min_number_of_routes_to_cluster = k
    if len(RetainedSet) >= min_number_of_routes_to_cluster:
        # cluster the retained set with K-Means
        time_temp = time()
        print(get_elapsed_time(), ":         Clustering retained set with K-Means")
        retainedSet_cluster_labels = cluster_retained_set(k)
        time_temp2 = time()
        cluster_retained_set_times.append(time_temp2 - time_temp)

        if len(retainedSet_cluster_labels) != 0:
            # add the new clusters to the set of compressed sets
            time_temp3 = time()
            add_miniclusters_to_compressed_sets(retainedSet_cluster_labels)
            time_temp4 = time()
            add_miniclusters_to_compressed_sets_times.append(time_temp4 - time_temp3)

            print(get_elapsed_time(), ":         Updating centroids of compressed sets")
            for cluster in CompressedSets:
                cluster.update_centroid()
            print(get_elapsed_time(), ":         -----")
    
    # h = 2 * number_of_clusters
    h = k
    min_number_of_routes_to_cluster_compressedsets = h*2

    if number_of_compressed_sets >= min_number_of_routes_to_cluster_compressedsets:
        # cluster the compressed sets with Hierarchical clustering
        print(get_elapsed_time(), ":         Clustering compressed sets with Hierarchical clustering")

        # cluster_compressed_sets(number_of_clusters)
        time_temp = time()
        cluster_compressed_sets(h)
        time_temp2 = time()
        cluster_compressed_sets_times.append(time_temp2 - time_temp)

        print(get_elapsed_time(), ":         Updating centroids of compressed sets")
        for cluster in CompressedSets:
            # TODO: centroid update here is different as we have other centroids in the routes[] array. We have to weight the distance between the routes and the centroid
            cluster.update_centroid()
        print(get_elapsed_time(), ":         -----")
    
def cluster_retained_set(k):
    global RetainedSet, CompressedSets

    distance_matrix = np.zeros((len(RetainedSet), len(RetainedSet)))
    city_indexes, cities_res, merch_indexes, merch_res = get_features_total(RetainedSet)

    print(get_elapsed_time(), ":             Calculating distance matrix with multithreading. RetainedSet size:", len(RetainedSet))
    for i in range(len(RetainedSet)):
        # pick all routes from the next one to the end
        for j in range(i + 1, len(RetainedSet)):
            distance_matrix[i][j] = distance_matrix[j][i] = custom_distance(city_indexes, cities_res[i], cities_res[j], merch_indexes, merch_res[i], merch_res[j])

    # calculate the distance matrix in multiple threads
    # def compute_distances(i, distances):
    #     # print(get_elapsed_time(), ":             Calculating distance matrix. Thread size:", len(thread_routes))
    #     for j in range(i + 1, len(RetainedSet)):
    #         distances[i][j] = distances[j][i] = custom_distance(city_indexes, cities_res[i], cities_res[j], merch_indexes, merch_res[i], merch_res[j])

    # with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
    #     # Give one route to each thread
    #     futures = {executor.submit(compute_distances, i, distance_matrix): i for i in range(len(RetainedSet))}
    
    # make the distance matrix symmetric
    # distance_matrix = distance_matrix + distance_matrix.T

    print(get_elapsed_time(), ":             Calling K-Means")
    try:
        # Perform K-Means clustering with the custom distance metric
        kmeans = KMeans(n_clusters=k, init='k-means++', algorithm='lloyd', n_init=10)
        kmeans.fit(distance_matrix)

        # Get cluster labels -> [0, 1, 1, 0] means route 0 has cluster index 0, route 1 has cluster index 1, etc.
        labels = kmeans.labels_
        #print("Cluster labels:", labels)

        return labels
    except ConvergenceWarning:
        print("ConvergenceWarning")
        return []

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
            #print("Adding route", RetainedSet[i]["id"], "to compressed set", indexes[labels[i]])
        else:
            new_retainedSet.append(RetainedSet[i])
            #print("Adding route", RetainedSet[i]["id"], "to new retained set")
    
    RetainedSet = new_retainedSet
            
def cluster_compressed_sets(k):
    global CompressedSets
    distance_matrix = np.zeros((len(CompressedSets), len(CompressedSets)))

    compressedSets_centroids = []
    for cluster in CompressedSets:
        compressedSets_centroids.append(cluster.centroid)

    print(get_elapsed_time(), ":             Calculating distance matrix with multithreading. CompressedSets size:", len(CompressedSets))
    city_indexes, cities_res, merch_indexes, merch_res = get_features_total(compressedSets_centroids)
    for i in range(len(CompressedSets)):
        # pick all routes from the next one to the end
        for j in range(i + 1, len(CompressedSets)):
            distance_matrix[i][j] = distance_matrix[j][i] = custom_distance(city_indexes, cities_res[i], cities_res[j], merch_indexes, merch_res[i], merch_res[j])

    # calculate the distance matrix in multiple threads
    # def compute_distances(i, distances):
    #     # print(get_elapsed_time(), ":             Calculating distance matrix. Thread size:", len(thread_routes))
    #     for j in range(i + 1, len(CompressedSets)):
    #         distances[i][j] = distances[j][i] = custom_distance(city_indexes, cities_res[i], cities_res[j], merch_indexes, merch_res[i], merch_res[j])

    # with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
    #     # Give one route to each thread
    #     futures = {executor.submit(compute_distances, i, distance_matrix): i for i in range(len(CompressedSets))}

    # make the distance matrix symmetric
    # distance_matrix = distance_matrix + distance_matrix.T

    print(get_elapsed_time(), ":             Calling Hierarchical clustering")
    # Perform hierarchical clustering
    clustering = AgglomerativeClustering(n_clusters=k, metric='precomputed', linkage='average')
    cluster_labels = clustering.fit_predict(distance_matrix)

    time_temp = time()
    update_CompressedSets(cluster_labels)
    time_temp2 = time()
    update_CompressedSets_times.append(time_temp2 - time_temp)

def update_CompressedSets(labels):
    print(get_elapsed_time(), ":                 Updating CompressedSets")
    global CompressedSets, number_of_compressed_sets

    new_number_of_compressed_sets = 0

    new_compressedSets = []

    labels_len = len(labels)
    indexes = {}
    for i in range(labels_len):
        if labels[i] in indexes:
            new_compressedSets[indexes[labels[i]]].add(CompressedSets[i].centroid, CompressedSets[i].size)
            new_compressedSets[indexes[labels[i]]].size += CompressedSets[i].size - 1
        else:
            indexes[labels[i]] = new_number_of_compressed_sets
            new_compressedSets.append(Cluster(CompressedSets[i].centroid, new_number_of_compressed_sets))
            new_compressedSets[indexes[labels[i]]].size += CompressedSets[i].size - 1
            new_number_of_compressed_sets += 1
        #print("Adding old cluster centroid", CompressedSets[i].centroid["id"], "to compressed set", indexes[labels[i]])
    
    number_of_compressed_sets = new_number_of_compressed_sets
    CompressedSets = new_compressedSets

def merge_compressed_sets_with_primary_clusters():
    global CompressedSets, Clusters
    if len(CompressedSets) == 0:
        return
    closest_cluster_means = []
    closest_clusters = []
    for compressedSet in CompressedSets:
        closest_cluster, closest_distance = find_closest_cluster(compressedSet.centroid)
        closest_clusters.append(closest_cluster)
        closest_cluster_means.append(closest_distance)

    clusters_threshold = np.average(closest_cluster_means)
    print(get_elapsed_time(), ":     Clustering compressed sets with primary clusters with threshold", clusters_threshold)
    
    counter = 0
    for compressedSet in CompressedSets:
        closest_cluster = closest_clusters[counter]
        closest_distance = closest_cluster_means[counter]
        counter += 1
        if closest_distance < clusters_threshold:
            # add the compressed set to the cluster
            print(get_elapsed_time(), ":     Adding compressed set", compressedSet.centroid["id"], "to cluster", closest_cluster, "with distance", closest_distance)
            Clusters[closest_cluster].add(compressedSet.centroid, compressedSet.size)
        
def write_results_to_file(results_file):
    counter = 0
    with open(results_file, "w") as f:
        f.write("[\n")
        for route in Clusters:
            json_output = json.dumps({"id": "ns" + str(counter), "route": route.centroid["route"]}, indent=4)
            f.write(json_output)
            if counter != len(Clusters) - 1:
                f.write(",\n")
            elif len(CompressedSets) != 0:
                f.write(",\n")
            else:
                f.write("\n")
            counter += 1
        for route in CompressedSets:
            json_output = json.dumps({"id": "ns" + str(counter), "route": route.centroid["route"]}, indent=4)
            f.write(json_output)
            if counter != len(CompressedSets) - 1:
                f.write(",\n")
            else:
                f.write("\n")
            counter += 1
        f.write("]\n")

if __name__ == "__main__":
    BFR("data/small2/standard_small.json", "data/small2/actual_normal_small.json", "results/recStandard_normal_small.json")
    # init_clusters("data/small2/standard_small.json")
    # write_results_to_file("results/recStandard_normal_small.json")