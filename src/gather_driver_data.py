# Read the text file
with open('data\small\drivers_data_small.txt', 'r') as file:
    lines = file.readlines()

# Initialize empty variables to store values
number_of_trips_changed = []
cities = []
merchandise_multivariate_means = []
merchandise_multivariate_covariances = []

# Parse lines and extract values
for line in lines:
    line = line.strip()
    if line.startswith('number_of_trips_changed'):
        number_of_trips_changed = [int(val) for val in line.split(':')[1].strip('[]').split(',')]
    elif line.startswith('cities'):
        cities = [float(val) for val in line.split(':')[1].strip('[]').split()]
    elif line.startswith('merchandise_multivariate_means'):
        merchandise_multivariate_means = [float(val) for val in line.split(':')[1].strip('[]').split()]
    elif line.startswith('merchandise_multivariate_covariances'):
        merchandise_multivariate_covariances = [float(val) for val in line.split(':')[1].strip('[]').split()]

# Create a dictionary to store the values
data = {
    "number_of_trips_changed": number_of_trips_changed,
    "cities": cities,
    "merchandise_multivariate_means": merchandise_multivariate_means,
    "merchandise_multivariate_covariances": merchandise_multivariate_covariances
}

# Display the obtained data
print(data)
