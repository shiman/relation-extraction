#!/usr/bin/python
# coding: utf-8

import os
import sys
import argparse
from time import time
import features
from util import *


def load_functions(feature_config):
    """
    Load feature functions
    """
    if feature_config == 'A':
        feature_functions = [x[1] for x in features.__dict__.items()
                             if x[0].endswith("_features")]
    else:
        feature_functions = list()
        for line in open(feature_config):
            if not line.startswith('#'):
                feature_functions.append(features.__dict__[line.strip()])
    return feature_functions


def apply_features(feat_config, data, out_folder, train):
    """
    apply all feature functions on the input and generate the training
    file

    :param feat_config: the txt file containing which feature functions
                     you want to use
    :param data: the data you want to apply feature functions on. e.g. "coref-trainset.gold"
    :param out_folder: where you want to store the extracted features. e.g. "MyDummyExperiment"
    :param train: whether the input data contains gold tags
    """
    result = list()
    data = load_mention_pairs(data)
    if train:
        result.append([x.label for x in data])
        outf = os.path.join(out_folder, "features.train")
    else:
        outf = os.path.join(out_folder, "features.test")
    for func in load_functions(feat_config):
        result.append(map(func, data))
    if len(result) == 0: return
    with open(outf, 'a') as f:
        for i in range(len(result[0])):
            line = ' '.join([col[i] for col in result])
            f.write(line + '\n')


def train(features, data, out_folder):
    """
    Train with specified threads and output folder

    :param features: the feature functions
    :param out_folder: the output directory of the model
    :param data: the input training data
    """
    apply_features(features, data, out_folder, train=True)
    cmd = "sh mallet-maxent-classifier.sh -train -model=%s -gold=%s" % \
          (os.path.join(out_folder, 'trained.model'),
           os.path.join(out_folder, 'features.train'))
    os.system(cmd)


def decode(features, data, out_folder):
    """
    Get the hypothesis on test data
    """
    apply_features(features, data, out_folder, train=False)
    cmd = 'sh mallet-maxent-classifier.sh -classify -model={0:s} -input={1:s} > {2:s}' \
        .format(os.path.join(out_folder, 'trained.model'),
                os.path.join(out_folder, 'features.test'),
                os.path.join(out_folder, 'hypothesis.prob'))
    os.system(cmd)


def evaluate(gold, out_folder):
    gold_tags = list()
    for line in open(gold):
        if line.strip():
            gold_tags.append(line.strip().split()[0])
    hypo_tags = list()
    for line in open(os.path.join(out_folder, "hypothesis.prob")):
        hypo_tags.append(line.strip().split()[0])
    gold_total = 0
    hypo_total = 0
    correct = 0
    assert len(gold_tags) == len(hypo_tags)
    for i in range(len(gold_tags)):
        if gold_tags[i] != 'no_rel': gold_total += 1
        if hypo_tags[i] != 'no_rel': hypo_total += 1
        if gold_tags[i] != 'no_rel' and hypo_tags[i] == gold_tags[i]: correct += 1
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
    parser = argparse.ArgumentParser(description="Run through a coreference resolution pipeline")
    parser.add_argument('--train', dest='trainset', help="path to the training data",
                        default='./data/rel-trainset.gold')
    parser.add_argument('--test', dest='testset', help="path to the test data", default='./data/rel-devset.raw')
    parser.add_argument('--gold', dest='testgold', help="path to the gold standard of the test data",
                        default='./data/rel-devset.gold')
    parser.add_argument('--features', dest='feature_config', help="path to the feature config", default='A')
    parser.add_argument('--task', dest='out_folder', help="specify a folder for the output and logs")
    args = parser.parse_args()
    if os.path.isdir(args.out_folder):
        print "ERROR: task(out_folder) already exists"
        exit()
    else:
        os.makedirs(args.out_folder)
    start_train = time()
    train(args.feature_config, args.trainset, args.out_folder)
    start_decode = time()
    decode(args.feature_config, args.testset, args.out_folder)
    start_eval = time()
    precision, recall, f = evaluate(args.testgold, args.out_folder)
    time_consumption = "Training: %.2f sec\nDecoding: %.2f sec" % \
                       ((start_decode - start_train), (start_eval - start_decode))
    evaluation = "Precision: %.2f\nRecall: %.2f\nF1: %.2f" % \
                 ((precision * 100), (recall * 100), (f * 100))
    if args.feature_config == 'A':
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
