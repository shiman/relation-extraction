#!/usr/bin/python
# coding: utf-8

from __future__ import with_statement
import os
from document import Document, MentionPair


"""
Some utilities to fetch useful information from the data
"""


def load_documents(postagged='./data/postagged-files',
                   parsed='./data/parsed-files',
                   dependency='./data/dep-files'):
    """
    Load all the postagged and parsed data into Document instances
    """
    raw_list = [x for x in os.listdir(postagged) if x.endswith('.tag')]
    d = dict()
    for filename in raw_list:
        root_name, _ = os.path.splitext(filename)
        d[root_name[:21]] = Document(root_name, postagged, parsed, dependency)
    return d


def load_mention_pairs(filename):
    """
    Load mention pairs
    """
    return [MentionPair(line) for line in open(filename)]


def read_lines(data_file):
    """ data file -> lines (lists) """
    with open(data_file, 'r') as f:
        for line in f.readlines():
            yield line
