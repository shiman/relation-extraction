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


def evaluate(gold_tags, hypo_tags):
    assert len(gold_tags) == len(hypo_tags)
    gold_total = 0
    hypo_total = 0
    correct = 0
    for i in range(len(gold_tags)):
        if gold_tags[i] != 'no_rel':
            gold_total += 1
        if hypo_tags[i] != 'no_rel':
            hypo_total += 1
        if gold_tags[i] != 'no_rel' and hypo_tags[i] == gold_tags[i]:
            correct += 1
    if hypo_total == 0:
        precision = 0.0
    else:
        precision = float(correct) / hypo_total
    recall = float(correct) / gold_total
    if (precision + recall) == 0:
        f1 = 0.0
    else:
        f1 = precision * recall * 2 / (precision + recall)
    print "GT:", gold_total, "HT:", hypo_total, "C:", correct
    return (precision, recall, f1)


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
        for feature in line.strip().split():
            key, value = feature.split('=')[0], feature.split('=')[1]
            feature_dict[key] = value
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
         ./kernels.py --train data/coref-trainset.gold \
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
                        help="path to the feature config", default='feature.txt')
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
    #classifier = svm.SVC(kernel=kernel_entity)  # potential MemoryError
    classifier = svm.SVC(kernel='linear')
    classifier.fit(X_train, y_train)
    
    devset = 'data/rel-devset.gold'
    feature_file_dev = args.out_folder+'/feature.dev'
    kernel_features(devset, args.feature_config, kernel_name,
                    feature_file_dev)
    X_dev = convert_features(load_features(feature_file_dev))
    y_dev = load_labels(devset)
    start_decode = time()
    predicted = classifier.predict(X_dev)
    # http://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html
    # example-classification-plot
    # digits-classification-py
    start_eval = time()
    precision, recall, f = evaluate(y_dev, predicted)
    time_consumption = "Training: %.2f sec\nDecoding: %.2f sec" % \
                       ((start_decode - start_train),
                        (start_eval - start_decode))
    evaluation = "Precision: %.2f\nRecall: %.2f\nF1: %.2f" % \
                 ((precision * 100), (recall * 100), (f * 100))
    # print("Classification report for classifier %s:\n%s\n"
    #       % (classifier, metrics.classification_report
    #          (y_dev, predicted)))

    # print("Confusion matrix:\n%s" % metrics.
    #       confusion_matrix(y_dev, predicted, y_dev))
    with open(os.path.join(args.out_folder, 'hype'), 'w') as hypotheses:
        for guess, gold in zip(predicted, y_dev):
            if guess != gold:
                hypotheses.write(gold + '   --------> ' + guess+'\n')
            else:
                hypotheses.write(gold + '\n')
    if args.feature_config == 'feature.txt':
        feat_log = "All feature functions applied"
    else:
        feat_log = open(args.feature_config).read()
    with open(os.path.join(args.out_folder, 'feature.config'), 'w') as f:
        f.write(feat_log)
    msg = time_consumption + '\n\n' + evaluation
    print msg
    with open(os.path.join(args.out_folder, "report.log"), 'w') as f:
        f.write(msg)


if __name__ == "__main__":
    main()
