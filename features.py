#!/usr/bin/python
# coding: utf-8

from document import *
from util import *

########## RESOURCES ##########
documents = load_documents()

###############################

########## Feature functions ##########
# Each feature function takes a single MentionPair instance
# and return its features as a string.
# Function name should always ends with `_features`

def location_features(mentionpair):
    return "SAME_SENT=" + \
           str(mentionpair.left.sent_index == mentionpair.right.sent_index)


###############################

if __name__ == '__main__':
    import doctest
    doctest.testmod()
