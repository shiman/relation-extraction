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


#References: lecture slides and reading papers
def entity_title_e1(mentionpair):
    """ check if left entity mention is titled """
    return "title_e1=" + str(mentionpair.left.string.istitle())
    

def entity_title_e2(mentionpair):
    """ check if right entity mention is titled """
    return "title_e2=" + str(mentionpair.right.string.istitle())
    
    
def entity_alpha_e1(mentionpair):
    """ check if 1st letter of left entity mention is alpha """
    return "alpha_e1=" + str(mentionpair.left.string[0].isalpha())
    

def entity_alpha_e2(mentionpair):
    """ check if 1st letter of right entity mention is alpha """
    return "alpha_e2=" + str(mentionpair.right.string[0].isalpha())
    

def entity_type_e1(mentionpair):
    """ entity type of the left entity mention """
    return "type_e1=" + mentionpair.left.netype


def entity_type_e2(mentionpair):
    """ -> entity type of the right entity mention """
    return "type_e2=" + mentionpair.right.netype


def normalize_pos(pos):
    """ -> normalize POS tag of entity mention """
    if pos[0] in 'NP':
        return pos
    elif pos[0] in 'CDJW':
        return pos[0]
    else:
        return 'O'


def entity_pos_e1(mentionpair):
    """ -> normalized POS tag of left entity mention """
    pos_e1 = mentionpair.left.get_postag(documents)[-1]
    return "pos_e1=" + normalize_pos(pos_e1) 


def entity_pos_e2(mentionpair):
    """ -> normalized POS tag of right entity mention """
    pos_e2 = mentionpair.right.get_postag(documents)[-1]
    return "pos_e2=" + normalize_pos(pos_e2)


def normalize_neighbor_pos(pos):
    """ normalize POS tag of neighbor token """
    if pos.isalpha():
        if pos=='POS':
            return pos
        elif pos.startswith('PR'):
            return pos[0]
        elif pos[0] in 'IJNVW':
            return pos[0]
        else:
            return '0'
    else:
        if pos==',':
            return pos
        else:
            return '1'


def entity_npos_e1(mentionpair):
    """ -> normalized POS tag of left entity mention's next token """
    npos_e1 = mentionpair.left.get_next_pos(documents)
    return "npos_e1=" + normalize_neighbor_pos(npos_e1)
    

def entity_ppos_e2(mentionpair):
    """ -> normalized POS tag of right entity mention's previous token """
    ppos_e2 = mentionpair.right.get_previous_pos(documents)
    return "ppos_e2=" + normalize_neighbor_pos(ppos_e2)
    

def entity_token_dist(mentionpair):
    """ -> number of tokens between two mentions """
    token_dist = mentionpair.right.indices[0] - \
                 mentionpair.left.indices[-1]
    if token_dist < 3:
        return "token_dist=" + str(token_dist)
    elif 3 <= token_dist < 5:
        return "token_dist=3-4"
    elif 5 <= token_dist < 7:
        return "token_dist=5-6"
    else:
        return "token_dist=7..."


#Reference:
#https://www.ldc.upenn.edu/sites/www.ldc.upenn.edu/files/english-rdc-v4.3.2.PDF
def entity_between_possessive(mentionpair):
    """ check if there is 's between two mentions """
    return "btw_pos=" + str('POS' in list\
                          (mentionpair.between_tags(documents)))


def entity_between_preposition(mentionpair):
    """ check if there is a preposition between two mentions """
    return "btw_prep=" + str('IN' in list\
                          (mentionpair.between_tags(documents)))


def entity_premod(mentionpair):
    """ check if there is a PreMod relation between two mentions """
    if entity_title_e1(mentionpair)=='title_e1=True' and \
       entity_title_e2(mentionpair)=='title_e2=False' and \
       entity_token_dist(mentionpair)=='token_dist=1':
        return "premod=True"
    else:
        return "premod=False"

def entity_formulaic(mentionpair):
    """ check if there is a formulaic consruction involving two mentions """
    temp = ' '.join(tag[:2] for tag in
                    mentionpair.between_tags(documents))
    return "formulaic=" + str(bool(re.search\
                                   (r', .*NN.* ,',temp)))

def entity_verbal(mentionpair):
    """ check if there is a VB...IN pattern between two mentions """
    temp = ' '.join(tag[:2] for tag in
                    mentionpair.between_tags(documents))
    return "formulaic=" + str(bool(re.search\
                                   (r'VB .*IN',temp)))


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
