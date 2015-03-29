import os
from nltk import ParentedTree
from dependency_tree import DepTree


class Document(object):
    """
    A document, representing an individual news file (a list of sentences).
    Empty lines are not kept. Document instances are supposed to be loaded as global
    variables in `features.py` to be used by feature functions.

    >>> doc = Document("APW20001001.2021.0521")
    >>> print doc.tagged_sents[1]
    Egypt-Assad_RB
    >>> tree = ParentedTree.fromstring("(S1 (NP (NN Egypt-Assad)))")
    >>> doc.parsed_sents[1] == tree
    True
    """

    def __init__(self, filename, postagged='./data/postagged-files',
                 parsed='./data/parsed-files',
                 dependency='./data/dep-files'):
        self.filename = filename
        postagged_file = os.path.join(postagged, filename+'.tag')
        parsed_file = os.path.join(parsed, filename+'.parse')
        dep_file = os.path.join(dependency, filename+'.parse.dep')
        self.tagged_sents = [x.strip() for x in open(postagged_file) if x.strip()]
        self.parsed_sents = [ParentedTree.fromstring(x) for x in open(parsed_file) if x.strip()]
        depsents = open(dep_file).read()
        self.dep_sents = [DepTree.fromstring(x)
                          for x in open(dep_file).read().strip().split('\n\r\n')
                          if x.strip()]
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
        postagged_tokens = documents[self.filename].tagged_sents[self.sent_index].split()
        postags = [postagged_tokens[i].split('_')[-1] for i in self.indices]
        return postags
        
    def get_previous_token(self, documents):
        """
        Get the previous token in the sentence
        :param documents: preloaded resources
        """
        if self.indices[0]==0:
            return "None"
        else:
            postagged_tokens = documents[self.filename].tagged_sents[self.sent_index].split()
            return postagged_tokens[self.indices[0]-1].split('_')[0]

    def get_next_token(self, documents):
        """
        Get the next token in the sentence
        :param documents: preloaded resources
        """
        postagged_tokens = documents[self.filename].tagged_sents[self.sent_index].split()
        if self.indices[-1]==len(postagged_tokens)-1:
            return "None"
        else:            
            return postagged_tokens[self.indices[-1]+1].split('_')[0]

    def get_previous_pos(self, documents):
        """
        Get the POS tag of the previous token in the sentence
        :param documents: preloaded resources
        """
        if self.indices[0]==0:
            return "0"
        else:
            postagged_tokens = documents[self.filename].tagged_sents[self.sent_index].split()
            return postagged_tokens[self.indices[0]-1].split('_')[1]

    def get_next_pos(self, documents):
        """
        Get the POS tag of the previous token in the sentence
        :param documents: preloaded resources
        """
        postagged_tokens = documents[self.filename].tagged_sents[self.sent_index].split()
        if self.indices[-1]==len(postagged_tokens)-1:
            return "0"
        else:            
            return postagged_tokens[self.indices[-1]+1].split('_')[1]

    def get_sentence_tokens(self, documents):
        '''
        Get all the tokens of the sentence where the mention occurrs
        :param documents: preloaded resources
        '''
        postagged_tokens = documents[self.filename].tagged_sents[self.sent_index].split()
        return ['_'.join(token.split('_')[:-1]) for token in postagged_tokens]

    def get_tree_dominator(self, documents):
        """
        Get the lowest tree node that dominates this mention
        """
        tree = documents[self.filename].parsed_sents[self.sent_index]
        subtree_position = tree.treeposition_spanning_leaves(self.indices[0], self.indices[-1]+1)
        subtree = tree[subtree_position]
        if not isinstance(subtree, ParentedTree):
            return tree[subtree_position[:-1]]
        return subtree

    def get_dep_subtree(self, documents):
        """
        Get the dependency subtree of this mention
        """
        sentence = documents[self.filename].dep_sents[self.sent_index]
        start = sentence.get(self.indices[0])
        end = sentence.get(self.indices[-1])
        return start.lca(end)

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

    def lca(self, documents):
        left = self.left.get_dep_subtree(documents)
        right = self.right.get_dep_subtree(documents)
        return left.lca(right)
        
    def between_sequence(self,documents):
        """ get tagged sentence fragment between two mention """
        postagged_tokens = documents[self.filename].tagged_sents[self.antecedent.sent_index].split()
        return postagged_tokens[self.left.indices[-1]+1:self.right.indices[0]]

    def between_tokens(self,documents):
        """ get tokens between two mention """
        for postagged_token in self.between_sequence(documents):
            yield postagged_token.split('_')[0]
            
    def between_tags(self,documents):
        """ get POS tags between two mention """
        for postagged_token in self.between_sequence(documents):
            yield tagged_token.split('_')[1]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
