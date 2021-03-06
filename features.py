#!/usr/bin/python
# coding: utf-8

from document import *
from util import *
import re
import json

# ######### RESOURCES ##########
documents = load_documents()

###############################

# ######### Feature functions ##########
# Each feature function takes a single MentionPair instance
# and return its features as a string.
# Function name should always ends with `_features`





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


def _normalize_pos(pos):
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
    return "pos_e1=" + _normalize_pos(pos_e1) 


def entity_pos_e2(mentionpair):
    """ -> normalized POS tag of right entity mention """
    pos_e2 = mentionpair.right.get_postag(documents)[-1]
    return "pos_e2=" + _normalize_pos(pos_e2)


def _normalize_neighbor_pos(pos):
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
    return "npos_e1=" + _normalize_neighbor_pos(npos_e1)
    

def entity_ppos_e2(mentionpair):
    """ -> normalized POS tag of right entity mention's previous token """
    ppos_e2 = mentionpair.right.get_previous_pos(documents)
    return "ppos_e2=" + _normalize_neighbor_pos(ppos_e2)
    

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


def location_features(mentionpair):
    return "SAME_SENT=" + \
           str(mentionpair.left.sent_index == mentionpair.right.sent_index)


def _get_between_words(mentionpair):
    if not (mentionpair.left.sent_index == mentionpair.right.sent_index):
        return ["NA"]
    left_index = mentionpair.left.indices[-1] + 1
    right_index = mentionpair.right.indices[0]
    sentence_tokens = mentionpair.left.get_sentence_tokens(documents)
    btw = sentence_tokens[left_index: right_index]
    return btw

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

def first_between(mentionpair):
    between = _get_between_words(mentionpair)
    if len(between)==0:
        return "FIRST_BETWEEN=NA"
    if len(between)==1:
        return "FIRST_BETWEEN=ONLY_{}".format(between[0])
    return "FIRST_BETWEEN={}".format(between[0])

def last_between(mentionpair):
    between = _get_between_words(mentionpair)
    if len(between)==0:
        return "LAST_BETWEEN=NA"
    if len(between)==1:
        return "LAST_BETWEEN=ONLY_{}".format(between[0])
    return "LAST_BETWEEN={}".format(between[-1])

def other_between(mentionpair):
    between = _get_between_words(mentionpair)
    # print between
    if len(between)>2:
        return "OTHER_BETWEEN={}".format('_'.join(between[1:-1]))
    else:
        return "OTHER_BETWEEN=NA"

def _right_is_subset_left(mentionpair):
    right_string = set(mentionpair.right.string.lower().split('_'))
    left_string = set(mentionpair.left.string.lower().split('_'))
    return right_string.issubset(left_string)

def _left_is_subset_right(mentionpair):
    right_string = set(mentionpair.right.string.lower().split('_'))
    left_string = set(mentionpair.left.string.lower().split('_'))
    return left_string.issubset(right_string)

def netype_plus_right_overlap(mentionpair):
    combo = [mentionpair.left.netype, mentionpair.right.netype]
    return "RIGHT_OVERLAP="+'_'.join(combo)+'_'+str(_right_is_subset_left(mentionpair))

def netype_plus_left_overlap(mentionpair):
    combo = [mentionpair.left.netype, mentionpair.right.netype]
    return "LEFT_OVERLAP="+'_'.join(combo)+'_'+str(_left_is_subset_right(mentionpair))

def is_overlap(mentionpair):
    combo = combo = [mentionpair.left.netype, mentionpair.right.netype]
    return "OVERLAP="+"|".join(combo)+str(_right_is_subset_left(mentionpair) or _left_is_subset_right(mentionpair))
#TODO

def combo_mention_level(mentionpair):
    """combination of mention levels"""
    right_pos = mentionpair.right.get_postag(documents)
    left_pos = mentionpair.left.get_postag(documents)
    
    if any(tag.startswith('NNP') for tag in right_pos) and any(tag.startswith('NNP') for tag in left_pos):
        return "MENTION_LEVEL_MATCH=NNP"

    elif any(tag.startswith('PR') for tag in right_pos) and any(tag.startswith('PR') for tag in left_pos):
        return "MENTION_LEVEL_MATCH=PRP"
    elif any(tag.startswith('NN') for tag in right_pos) and any(tag.startswith('NN') for tag in left_pos):
        return "MENTION_LEVEL_MATCH=NN"
    else:
        return "MENTION_LEVEL_MATCH=NA"

def combo_words(mentionpair):
    """combo of mentions strings"""
    return "WORD_COMBO={}|{}".format(mentionpair.left.string, mentionpair.right.string)

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


def entity_between_preposition_loc(mentionpair):
    """ check if there is a location preposition between two mentions """
    prep_loc = {'at','on','in'}
    temp = False
    for token in mentionpair.between_tokens(documents):
        if token in prep_loc:
            temp = True
            break
    return "prep_loc=" + str(temp)


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


social = dict()
for line in read_lines('lists/social.txt'):
    tokens = line.split()
    social[tokens[0]] = tokens[1:]

def _social_status(mention):
    """ check if mention belong to any social relations """
    temp = 'NONE'
    for k in social:
        for v in social[k]:
            if v in mention:
                temp = k
                break
        if temp!='NONE':
            break
    return temp 

def entity_social(mentionpair):
    """ look for potential PER.SOC relations """
    temp = 'NONE'
    if mentionpair.left.netype=='PER' and \
       mentionpair.right.netype=='PER':
        if _social_status(mentionpair.left.string)!='NONE':
            temp = _social_status(mentionpair.left.string)
        elif _social_status(mentionpair.right.string)!='NONE':
            temp = _social_status(mentionpair.right.string)
    return "social=" + temp

# json format lists
def _load_list(list_file):
    """ load the external name list into memory """
    with open(list_file, 'r') as f:
        words = set(json.load(f))
        return words

def _belong(mention,list_file):
    """ check if mention belong to list """
    temp = False
    for w in _load_list(list_file):
        if w in mention.lower():
            temp = True
            break
    return temp
            
def entity_geo(mentionpair):
    """ check if mentions are geographical places """
    geo_e1,geo_e2 = False, False
    if _belong(mentionpair.left.string,'lists/GPE.txt'):
        geo_e1 = True
    if _belong(mentionpair.right.string,'lists/GPE.txt'):
        geo_e2 = True
    return "geo=" + str(geo_e1) + '_' + str(geo_e2)

def entity_geo_e1(mentionpair):
    """ check if left mention is geographical place """
    geo_e1 = False
    if _belong(mentionpair.left.string,'lists/GPE.txt'):
        geo_e1 = True
    return "geo_e1=" + str(geo_e1)

def entity_geo_e2(mentionpair):
    """ check if right mention is geographical place """
    geo_e2 = False
    if _belong(mentionpair.right.string,'lists/GPE.txt'):
        geo_e2 = True
    return "geo_e2=" + str(geo_e2)

employment = dict()
for line in read_lines('lists/employment.txt'):
    tokens = line.split()
    employment[tokens[0]] = tokens[1:]

def _employment_status(mention):
    """ check if mention belong to any employment relations """
    temp = 'NONE'
    for k in employment:
        for v in employment[k]:
            if v in mention.lower():
                temp = k
                break
        if temp!='NONE':
            break
    return temp

def entity_employment_e1(mentionpair):
    """ look for potential PER.SOC relations """
    temp = 'NONE'
    if mentionpair.left.netype=='PER':
        if _employment_status(mentionpair.left.string)!='NONE':
            temp = _employment_status(mentionpair.left.string)
    return "employ_e1=" + temp

def entity_employment_e2(mentionpair):
    """ look for potential PER.SOC relations """
    temp = 'NONE'
    if mentionpair.right.netype=='PER':
        if _employment_status(mentionpair.right.string)!='NONE':
            temp = _employment_status(mentionpair.right.string)
    return "employ_e2=" + temp

ideology = list()
for line in read_lines('lists/ideology.txt'):
    tokens = line.split()
    ideology.extend(tokens)

def _ideology_status(mention):
    """ check if mention belong to any ideology relations """
    temp = 'NONE'
    for token in ideology:
        if token in mention:
            temp = 'IDEO'
            break
    return temp

def entity_ideology_e1(mentionpair):
    """ look for potential ideology relations """
    temp = 'NONE'
    token_dist = mentionpair.right.indices[0] - \
                 mentionpair.left.indices[-1]
    if token_dist<=3:
        temp = _ideology_status(mentionpair.left.string)
    return "ideo_e1=" + temp

def entity_ideology_e2(mentionpair):
    """ look for potential ideology relations """
    temp = 'NONE'
    token_dist = mentionpair.right.indices[0] - \
                 mentionpair.left.indices[-1]
    if token_dist<=3:
        temp = _ideology_status(mentionpair.right.string)
    return "ideo_e2=" + temp

part_whole = list()
for line in read_lines('lists/part-whole.txt'):
    tokens = line.split()
    part_whole.extend(tokens)

def _part_whole_status(mention):
    """ check if mention belong to any part-whole relations """
    temp = 'NONE'
    for token in part_whole:
        if token in mention.lower():
            temp = 'PTWL'
            break
    return temp

def entity_part_whole_e1(mentionpair):
    """ look for potential part-whole relations """
    return "ptwl_e1=" + _part_whole_status(mentionpair.left.string)

def entity_part_whole_e2(mentionpair):
    """ look for potential part-whole relations """
    return "ptwl_e2=" + _part_whole_status(mentionpair.right.string)


# FEATURES - KERNEL - TREE - SYNTACTIC



def syntactic_pt(mentionpair):
    """
    -> number of common sub-trees of Path-enclosed Tree
    """
    

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


# FEATURES - KERNEL _ TREE - DEPENDENCY
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
    dep = '_'.join([x.token for x in tree.children])
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


# ##############################

if __name__ == '__main__':
    import doctest
    doctest.testmod()
