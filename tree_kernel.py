from collections import namedtuple
import sys
from sklearn import svm
import numpy as np
from nltk.corpus import wordnet as wn
from util import load_documents
from util import load_mention_pairs
from kernels import load_labels


documents = load_documents()


Feature = namedtuple('Feature', ['word', 'pos', 'cpos', 'chunktag', 'hypernym', 'netypes'])
Instance = namedtuple('Instance', ['tree', 'sent_index', 'filename'])


def features(t, sent_index, filename):
    """
    Get the features of a dep tree
    features include:
    word, POS, Collapsed_POS, ChunkTag, WordNet_Hypernym
    """
    word = t.token.lower()
    parse_tree = documents[filename].parsed_sents[sent_index]
    pos = parse_tree.pos()[t.index]
    collapsed = pos[0]
    treeposition = parse_tree.treeposition_spanning_leaves(t.index, t.index+1)[:-2]
    chunktag = parse_tree[treeposition].label()
    if chunktag.startswith("N"): chunktag = 'NP'
    elif chunktag.startswith("V"): chunktag = "VP"
    elif chunktag.startswith("P"): chunktag = "VP"
    else: chunktag = 'OTHER'
    try:
        hypernym = wn.synsets(word).hypernyms()[0]
    except Exception:
        hypernym = None
    try:
        netypes = t.netypes
    except Exception:
        netypes = None
    return Feature(word, pos, collapsed, chunktag, hypernym, netypes)


def match(f1, f2):
    """chech if two feature vectors match"""
    return f1.cpos == f2.cpos and f1.netypes == f2.netypes

def common_feature_values(f1, f2):
    """the similarity function s(t_i, t_i)"""
    return sum([f1[i] == f2[i] for i in range(len(f1))])


def culotta_sorensen(t1, t2, sent_index1, sent_index2,
                     filename1, filename2, lmd=0.5, decay=0):
    """
    kernel function from slide 12 (not exactly)
    """
    if t1 is None or t2 is None:
        return 0.0
    if t1.features is not None:
        f1 = t1.features
    else:
        f1 = features(t1, sent_index1, filename1)
    if t2.features is not None:
        f2 = t2.features
    else:
        f2 = features(t2, sent_index2, filename2)
    t1.features = f1
    t2.features = f2
    if not match(f1, f2):
        return 0.0
    else:
        score = common_feature_values(f1, f2)
        for c1 in t1.children:
            for c2 in t2.children:
                score += lmd ** decay * culotta_sorensen(c1, c2, sent_index1, sent_index2,
                                                         filename1, filename2, lmd, decay+1)
        return score


def get_gram_matrix(data1, data2, saveto=''):
    mentionpairs_x = load_mention_pairs(data1)
    instances_x = [Instance(m.lca(documents), m.left.sent_index, m.left.filename)
                   for m in mentionpairs_x]
    if data2 is None:
        mentionpairs_y = mentionpairs_x
        instances_y = instances_x
    else:
        mentionpairs_y = load_mention_pairs(data2)
        instances_y = [Instance(m.lca(documents), m.left.sent_index, m.left.filename)
                       for m in mentionpairs_y]
    size = (len(mentionpairs_x), len(mentionpairs_y))
    gram = np.zeros(size)
    for i, a in enumerate(instances_x):
        for j, b in enumerate(instances_y):
            sys.stderr.write('\r')
            sys.stderr.write("({}, {})".format(i, j))
            score = culotta_sorensen(a.tree, b.tree, a.sent_index, b.sent_index,
                                     a.filename, b.filename)
            sys.stderr.write(' : {}'.format(score))
            gram[i,j] = score
    sys.stderr.write('\n')
    if saveto:
        np.save(saveto, gram)
    return gram


if __name__ == '__main__':
    gram = get_gram_matrix('./data/rel-trainset.gold', None, 'gram_train.npy')
    Y = load_labels('./data/rel-train.gold')
    clf = svm.SVC(kernel='precomputed')
    clf.fit(gram, Y)
    test_gram = get_gram_matrix('./data/rel-testset.gold', 'gram_test.npy')
    hypothesis = clf.predict(test_gram)
    with open('kernel_based.hyp', 'a') as f:
        for x in hypothesis:
            f.write(x + '\n')

