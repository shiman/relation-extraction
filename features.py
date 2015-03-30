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
    btw = sentence_tokens[left_index: right_index]
    return "BETWEEN_WORD={} BTW_NUM={}".\
        format('_'.join(btw), len(btw))


def left_words(mentionpair):
    return "LEFT={}".format(mentionpair.left.string)
def right_words(mentionpair):
    return "RIGHT={}".format(mentionpair.right.string)

def surrounding(mentionpair):
    """Words before left and after right"""
    if mentionpair.left.indices[0] == 0:
        before = "NA"
    else:
        i = mentionpair.left.indices[0] - 1
        before = mentionpair.left.get_sentence_tokens(documents)[i]
    right_sent = mentionpair.right.get_sentence_tokens(documents)
    if mentionpair.right.indices[-1] == len(right_sent):
        after = "NA"
    else:
        after = right_sent[mentionpair.right.indices[-1]]
    return "BEFORE={} AFTER={}".format(before, after)

def combo_type(mentionpair):
    """combination of netype"""
    return "TYPE_COMBO={}|{}".format(mentionpair.left.netype,
                                  mentionpair.right.netype)

#TODO
def combo_mention_level(mentionpair):
    """combination of mention levels"""
    pass

def _dependent(mention):
    return '_'.join([c.token for c in mention.get_dep_subtree(documents).children])

def dependent_and_netype(mentionpair):
    """combination of netype and dependent word"""
    left = _dependent(mentionpair.left) + '|' + mentionpair.left.netype
    right = _dependent(mentionpair.right) + '|' + mentionpair.right.netype
    return "LEFT_DEPNTYPE={} RIGHT_DEPNTYPE={}".format(left, right)

def _dep_surrouding(mention):
    """combination of dependent word and head word"""
    tree = mention.get_dep_subtree(documents)
    dep = ' '.join([x.token for x in tree.children])
    if tree.parent:
        head = tree.parent.token
    else:
        head = 'None'
    return "{}|{}".format(dep, head)

def dep_surrounding(mentionpair):
    """combination of head word and dependent word"""
    left = _dep_surrouding(mentionpair.left)
    right = _dep_surrouding(mentionpair.right)
    return "LEFT_DEP_SRD={} RIGHT_DEP_SRD={}".format(left, right)

def lca_type(mentionpair):
    """combination of left&right and LCA==(NP|PP|VP)"""
    netypes = "{}_{}".format(mentionpair.left.netype, mentionpair.right.netype)
    indices = sorted(mentionpair.left.indices + mentionpair.right.indices)
    if mentionpair.left.sent_index != mentionpair.right.sent_index:
        lca = 'NA'
    else:
        tree = documents[mentionpair.filename].parsed_sents[mentionpair.left.sent_index]
        lca_pos = tree.treeposition_spanning_leaves(indices[0], indices[-1]+1)
        tree = tree[lca_pos]
        if tree.label().startswith("NP"):
            lca = "NP"
        elif tree.label().startswith("VP"):
            lca = "VP"
        elif tree.label().startswith("PP"):
            lca = "PP"
        else:
            lca = "OTHER"
    return "LCATYPE={}|{}".format(netypes, lca)

def path_between(mentionpair):
    """path of phrase labels connecting left and right"""
    if mentionpair.left.sent_index != mentionpair.right.sent_index:
        path = "NA"
    else:
        tree = documents[mentionpair.filename].parsed_sents[mentionpair.left.sent_index]
        l_tree = mentionpair.left.get_tree_dominator(documents)
        r_tree = mentionpair.right.get_tree_dominator(documents)
        l_pos = l_tree.treeposition()
        r_pos = r_tree.treeposition()
        for i in range(len(min(l_pos, r_pos))):
            if l_pos[i] != r_pos[i]:
                break
        lca = tree[l_pos[:i]]
        left_path = list()
        while l_tree != lca:
            left_path.append(l_tree.label())
            l_tree = l_tree.parent()
        right_path = list()
        while r_tree != lca:
            right_path.append(r_tree.label())
            r_tree = r_tree.parent()
        right_path.reverse()
        path = '{}>{}<{}'.format('>'.join(left_path), lca.label(), '<'.join(right_path))
    return "PATH_BTW={}".format(path)


# FEATURES - KERNEL - ENTITY


def entity_type_e1(mentionpair):
    """
    -> entity type of the first entity mention
    """
    return "type_e1=" + mentionpair.left.netype


def entity_type_e2(mentionpair):
    """
    -> entity type of the second entity mention
    """
    return "type_e2=" + mentionpair.right.netype


def entity_token_dist(mentionpair):
    """
    -> number of tokens between two mentions
    """
    token_dist = mentionpair.right.indices[0] - \
        mentionpair.left.indices[-1] + 1
    if token_dist < 3:
        return "token_dist=" + str(token_dist)
    else:
        return "token_dist=n"

# FEATURES - KERNEL - TREE - SYNTACTIC


def syntactic_pt(mentionpair):
    """
    -> number of common sub-trees of Path-enclosed Tree
    """
    pass

# FEATURES - KERNEL _ TREE - DEPENDENCY

# ##############################

if __name__ == '__main__':
    import doctest
    doctest.testmod()
