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
    
# FEATURES - KERNEL - ENTITY
def entity_type_e1(rel):
    """
    -> entity type of the first entity mention
    """
    return "type_e1=" + rel.antecedent.netype

def entity_type_e2(rel):
    """
    -> entity type of the second entity mention
    """
    return "type_e2=" + rel.anaphor.netype

def entity_token_dist(rel):
    """
    -> number of tokens between two mentions
    """
    token_dist = rel.anaphor.indices[0] - \
                 rel.antecedent.indices[-1]
    if token_dist<3:
        return "token_dist=" + str(token_dist)
    else:
        return  "token_dist=n"

# FEATURES - KERNEL - TREE - SYNTACTIC
def syntactic_pt(rel):
    """
    -> number of common sub-trees of Path-enclosed Tree
    """
    pass

# FEATURES - KERNEL _ TREE - DEPENDENCY

# ##############################

if __name__ == '__main__':
    import doctest
    doctest.testmod()
