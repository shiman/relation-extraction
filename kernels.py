#!/usr/bin/python
# coding: utf-8

from util import *
import os
import features
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm, metrics
import numpy as np
import argparse
import sys
import os
from time import time


def _match(t1, t2):
    pass


def get_features(config_file, kernel_name):
    """ get names of feature functions of a kernel """
    feature_functions = list()
    for line in open(config_file):
        if line.startswith(kernel_name):
            feature_functions.append(features.
                                     __dict__[line.strip()])
    return feature_functions


def kernel_features(data, config_file, kernel_name, output_file):
    """ write features of a kernel to txt file """
    output = list()
    rels = load_mention_pairs(data)
    for func in get_features(config_file, kernel_name):
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


def kernel_entity(x, y):
    """ linear kernel for entity kernel features """
    x = x.astype(np.uint8)
    y = y.astype(np.uint8)
    return np.dot(x, y.T)


def main():
    h = "USAGE: \
         ./pipeline.py --train data/coref-trainset.gold \
                   --test data/coref-devset.notag \
                   --gold data/coref-devset.gold \
                   --feature feature.txt \
                   --task MyDummyExperiment"
    if len(sys.argv) == 1:
        print h
        exit()

    parser = argparse.ArgumentParser(
        description="Run through a coreference resolution pipeline")
    parser.add_argument('--train', dest='trainset', help="path to the training data",
                        default='./data/rel-trainset.gold')
    parser.add_argument(
        '--test', dest='testset', help="path to the test data", default='./data/rel-devset.raw')
    parser.add_argument('--gold', dest='testgold', help="path to the gold standard of the test data",
                        default='./data/rel-devset.gold')
    parser.add_argument('--features', dest='feature_config',
                        help="path to the feature config", default='A')
    parser.add_argument(
        '--task', dest='out_folder', help="specify a folder for the output and logs", default="DummyExperiment")
    args = parser.parse_args()
    if os.path.isdir(args.out_folder):
        print "ERROR: task(out_folder) already exists"
        exit()
    else:
        os.makedirs(args.out_folder)
    start_train = time()

    kernel_name = 'entity'

    kernel_features(args.trainset, args.feature_config, kernel_name,
                    args.out_folder+'/feature.train')

    X_train = convert_features(load_features(args.out_folder+'/feature.train'))
    y_train = load_labels(args.trainset)
    # entity kernel
    c = svm.SVC(kernel=kernel_entity)
    # I put 5000 here because I encounter MemoryError on my computer
    c.fit(X_train, y_train)
    devset = 'data/rel-devset.gold'

    feature_file_dev = args.out_folder+'/feature.dev'
    kernel_features(devset, args.feature_config, kernel_name,
                    feature_file_dev)
    X_dev = convert_features(load_features(feature_file_dev))
    y_dev = load_labels(devset)
    predicted = c.predict(X_dev)
    # http://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html
    # example-classification-plot
    # digits-classification-py
    print("Classification report for classifier %s:\n%s\n"
          % (c, metrics.classification_report
             (y_dev, predicted)))
    print("Confusion matrix:\n%s" % metrics.
          confusion_matrix(y_dev, predicted))

if __name__ == "__main__":
    main()
