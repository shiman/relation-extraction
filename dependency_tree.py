from itertools import takewhile


class DepTree(object):
    """
    A dependency tree object working with stanford parser
    tree format
    Note that this implementation assumes that each child
    has only one parent
    >>> s = '''poss(dog-2, My-1)
    ... nsubj(likes-4, dog-2)
    ... advmod(likes-4, also-3)
    ... root(ROOT-0, likes-4)
    ... xcomp(likes-4, eating-5)
    ... dobj(eating-5, sausage-6)'''
    >>> tree = DepTree.fromstring(s)
    >>> print tree
    ROOT-0, likes-4
    likes-4, dog-2
    dog-2, My-1
    likes-4, also-3
    likes-4, eating-5
    eating-5, sausage-6
    >>> dog = tree.get(1)
    >>> print dog.token
    dog
    >>> dog.left()
    [DepTree<My>]
    >>> dog.right()
    []
    >>> dog.parent
    DepTree<likes>
    >>> sausage = tree.get(5)
    >>> dog.lca(sausage)
    DepTree<likes>
    """

    def __init__(self, token, index=None):
        self.token = token
        self._children = list()
        self._parent = None
        self._index = index

    def is_root(self):
        return self._parent is None

    @property
    def index(self):
        """the word index, starting from zero,
        which means that the original zero index (ROOT) is
        excluded here"""
        if self.is_root():
            return None
        return self._index - 1

    def get(self, index):
        """Get the subtree of a specific word index"""
        for subtree in self.subtrees():
            if subtree.index == index:
                return subtree
        return None

    def subtrees(self):
        """Recursively traverse all subtrees"""
        yield self
        for child in self.children:
            for subtree in child.subtrees():
                yield subtree

    def tokens(self):
        return ' '.join(x.token for x in self.subtrees())

    def left(self):
        """Subtrees left-arced to this tree"""
        return [x for x in self.children if x.index < self.index]

    def right(self):
        """Subtrees right-arced to this tree"""
        return [x for x in self.children if x.index > self.index]

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, mother_tree):
        assert isinstance(mother_tree, DepTree)
        assert self.parent is None
        self._parent = mother_tree
        if self not in mother_tree.children:
            mother_tree.add_child(self)

    @property
    def children(self):
        return self._children

    def add_child(self, subtree):
        assert isinstance(subtree, DepTree)
        assert subtree.parent is None
        self._children.append(subtree)
        subtree.parent = self

    def __eq__(self, other):
        if not isinstance(other, DepTree):
            return False
        return self.token == other.token and self.index == other.index

    def __hash__(self):
        return hash((self.token, self.index))

    def lca(self, t):
        """
        get the lowest common ancestor, assuming `self` and `t`
        are from the same sentence
        :param t: another DepTree instance
        """
        assert isinstance(t, DepTree)
        if self == t:
            return t
        path_to_root = set()
        cur = self
        while not cur.is_root():
            path_to_root.add(cur)
            cur = cur.parent
        cur = t
        while not cur.is_root():
            if cur.parent in path_to_root:
                return cur.parent
            cur = cur.parent
        return cur

    def _get_pairs(self):
        pairs = list()
        for c in self.children:
            parent = "{0:s}-{1:d}".format(self.token, self._index)
            child = "{0:s}-{1:d}".format(c.token, c._index)
            pairs.append(parent + ', ' + child)
            pairs += c._get_pairs()
        return pairs

    def __repr__(self):
        return "DepTree<{0}>".format(self.token)

    def __str__(self):
        pairs = self._get_pairs()
        return '\n'.join(pairs)

    @classmethod
    def fromstring(cls, s):
        """
        Construct a DepTree from Stanford Parser format string
        """
        leaves = dict()
        for line in s.strip().split('\n'):
            parent, child = line[line.find('(') + 1: -1].split(', ')
            if parent not in leaves:
                _parts = parent.split('-')
                parent_token = '-'.join(_parts[:-1])
                parent_index = _parts[-1]
                parent_node = cls(parent_token, index=int(parent_index))
                leaves[parent] = parent_node
            if child not in leaves:
                _parts = child.split('-')
                child_token = '-'.join(_parts[:-1])
                child_index = _parts[-1]
                child_node = cls(child_token, index=int(child_index))
                leaves[child] = child_node
            leaves[parent].add_child(leaves[child])
        return leaves['ROOT-0']


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    # s = '''poss(dog-2, My-1)
    #     nsubj(likes-4, dog-2)
    #     advmod(likes-4, also-3)
    #     root(ROOT-0, likes-4)
    #     xcomp(likes-4, eating-5)
    #     dobj(eating-5, sausage-6)'''
    # tree = DepTree.fromstring(s)
    # dog = tree.get(1)
    # sausage = tree.get(5)
    # dog.lca(sausage)