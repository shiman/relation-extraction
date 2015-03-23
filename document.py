import os
from nltk import ParentedTree


class Document(object):
    """
    A document, representing an individual news file (a list of sentences).
    Empty lines are not kept. Document instances are supposed to be loaded as global
    vairables in `features.py` to be used by feature functions.

    >>> doc = Document("APW20001001.2021.0521.head.rel.tokenized.raw")
    >>> print doc.tagged_sents[1]
    Egypt-Assad_RB
    >>> tree = ParentedTree.fromstring("(S1 (NP (NN Egypt-Assad)))")
    >>> doc.parsed_sents[1] == tree
    True
    """

    def __init__(self, filename, postagged='./data/postagged-files',
                 parsed='./data/parsed-files'):
        self.filename = filename
        postagged_file = os.path.join(postagged, filename+'.tag')
        parsed_file = os.path.join(parsed, filename+'.parse')
        self.tagged_sents = [x.strip() for x in open(postagged_file) if x.strip()]
        self.parsed_sents = [ParentedTree.fromstring(x) for x in open(parsed_file) if x.strip()]
        assert len(self.tagged_sents) == len(self.parsed_sents)

    def __len__(self):
        return len(self.tagged_sents)

    def __str__(self):
        return self.filename


class Mention(object):
    """
    A mention instance
    """

    def __init__(self, string, start, end,
                 line_no, filename, netype):
        self.string = string
        self.sent_index = line_no  # sentence index
        self.filename = filename
        self.netype = netype
        self.indices = range(start, end)  # token indices

    def get_postag(self, documents):
        """
        Get the POS tags for this mention
        :param document: preloaded resources
        """
        postagged_tokens = documents[self.filename].tagged_sents[self.sent_index]
        postags = [postagged_tokens[i].split('_')[-1] for i in self.indices]
        return postags

    def get_tree_donimator(self, documents):
        """
        Get the lowest tree node that dominates this mention
        """
        tree = documents[self.filename].parsed_sents[self.sent_index]
        subtree_position = tree.treeposition_spanning_leaves(self.indices[0], self.indices[-1]+1)
        subtree = tree[subtree_position]
        if not isinstance(subtree, ParentedTree):
            return tree[subtree_position[:-1]]
        return tree

    def __str__(self):
        return "sentence_index: %d\ntoken_indices: %s\nNE_type: %s\nstr: %s" % \
               (self.sent_index, ' '.join([str(x) for x in self.indices]),
                self.netype, self.string)


class MentionPair(object):
    """
    A coreference instance. Contains the markable pair, as well as a link
    to the original file

    >>> raw_line = 'PHYS.Part-Whole	APW20001001.2021.0521	3	0	1	GPE	15-1	CAIRO	3	2	3	GPE	43-86	Egypt'
    >>> coref_instance = MentionPair(raw_line)
    >>> print coref_instance.left
    sentence_index: 3
    token_indices: 0
    NE_type: GPE
    str: CAIRO
    >>> print coref_instance.right
    sentence_index: 3
    token_indices: 2
    NE_type: GPE
    str: Egypt
    """

    def __init__(self, data, isgold=True):
        """
        Parse a line of raw data into Coreference Document
        """
        tokens = data.strip().split()
        if len(tokens) == 14:
            self.label = tokens[0]
            tokens = tokens[1:]
        else:
            self.label = None
        assert len(tokens) > 10
        filename = tokens[0]
        self.left = Mention(tokens[6], int(tokens[2]), int(tokens[3]),
                            int(tokens[1]), filename, tokens[4])
        self.right = Mention(tokens[12], int(tokens[8]), int(tokens[9]),
                             int(tokens[7]), filename, tokens[10])
        self.filename = filename


if __name__ == '__main__':
    import doctest
    doctest.testmod()
