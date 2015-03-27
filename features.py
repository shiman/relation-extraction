#!/usr/bin/python
# coding: utf-8

from document import *
from util import *

# ######### RESOURCES ##########
documents = load_documents()

###############################

# ######### Feature functions ##########
# Each feature function takes a single MentionPair instance
# and return its features as a string.
# Function name should always ends with `_features`


def location_features(mentionpair):
    return "SAME_SENT=" + \
           str(mentionpair.left.sent_index == mentionpair.right.sent_index)


def between_words(mentionpair):
    if not (mentionpair.left.sent_index == mentionpair.right.sent_index):
        return "BETWEEN_WORD=NA"
    left_index = mentionpair.left.indices[-1] + 1
    right_index = mentionpair.right.indices[0]
    sentence_tokens = mentionpair.left.get_sentence_tokens(documents)
    return "BETWEEN_WORD={}".format('_'.join(sentence_tokens[left_index: right_index]))

# ##############################

if __name__ == '__main__':
    import doctest
    doctest.testmod()
