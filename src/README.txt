How to run:

Step 1: Install the dependencies
Python 3.6, ijson, numpy, scikit-learn are needed to run the code. 
You can install them using pip: pip install ijson numpy scikit-learn or conda: conda install ijson numpy scikit-learn
To install python 3.6, please refer to https://www.python.org/downloads/

Step 2: Run the code
To run the algorithm on custom datasets, please run the following command:
python3 src/main.py [path to the standard route file] [path to the actual route file]

To instead run the algorithm on the provided synthetic datasets, please run the following command:
python3 src/main.py test [dataset type]

with dataset type being one of the following:
    - small
    - normal_small
    - big
    - normal_big
