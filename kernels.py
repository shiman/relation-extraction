#!/usr/bin/python
# coding: utf-8

from util import *
import os
import features
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm, metrics
import numpy as np

def _match(t1, t2):
    pass

def get_features(config_file,kernel_name):
    """ get names of feature functions of a kernel """
    feature_functions = list()
    for line in open(config_file):
        if line.startswith(kernel_name):
            feature_functions.append(features.\
                                     __dict__[line.strip()])
    return feature_functions

def kernel_features(data,config_file,kernel_name,output_file):
    """ write features of a kernel to txt file """
    output = list()
    rels = load_mention_pairs(data)    
    for func in get_features(config_file,kernel_name):
        output.append(map(func, rels))
    if len(output) == 0:
        return
    if os.path.isfile(output_file):
        os.remove(output_file)
    with open(output_file, 'a') as f:
        for i in range(len(output[0])):
            line = ' '.join([col[i] for col in output])
            f.write(line + '\n')

def load_features(feature_file):
    """ load features from txt file """
    features = list()
    for line in read_lines(feature_file):
        feature_dict = dict()
        for feature in line.split():            
            temp = feature.split('=')
            feature_dict[temp[0]] = temp[1]
        features.append(feature_dict)
    return features
        
def convert_features(features):
    """ convert features to SVM input format """
    vec = DictVectorizer()
    return vec.fit_transform(features).toarray()

def load_labels(data):
    """ -> load labels from data to list """
    rels = load_mention_pairs(data)
    return [x.label for x in rels]

# KERNELS
def kernel_entity(x,y):
    """ linear kernel for entity kernel features """
    x = x.astype(np.uint8)
    y = y.astype(np.uint8)
    return np.dot(x,y.T)

def main():
    trainset = 'data/rel-trainset.gold'
    config_file = 'feature.config'
    path_train = '20150328/feature.train'
    kernel_name = 'entity'
    feature_file_train = path_train + '.' + kernel_name
    kernel_features(trainset,config_file,kernel_name,\
                    feature_file_train)    
    X_train = convert_features(load_features(feature_file_train))
    y_train = load_labels(trainset)
    # entity kernel
    c = svm.SVC(kernel=kernel_entity)
    # I put 5000 here because I encounter MemoryError on my computer
    c.fit(X_train[:5000],y_train[:5000])
    devset = 'data/rel-devset.gold'
    path_dev = '20150328/feature.dev'
    feature_file_dev = path_dev + '.' + kernel_name
    kernel_features(devset,config_file,kernel_name,\
                    feature_file_dev)
    X_dev = convert_features(load_features(feature_file_dev))
    y_dev = load_labels(devset)
    predicted = c.predict(X_dev)
    #http://scikit-learn.org/stable/auto_examples/classification/
    #plot_digits_classification.html#example-classification-plot
    #-digits-classification-py
    print("Classification report for classifier %s:\n%s\n"
          % (c, metrics.classification_report\
             (y_dev, predicted)))
    print("Confusion matrix:\n%s" % metrics.\
          confusion_matrix(y_dev, predicted))

if __name__ == "__main__":
    main()
