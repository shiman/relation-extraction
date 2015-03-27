#TODO fromstring() not working yet
class DepTree(object):
    """
    >>> s = '''poss(dog-2, My-1)
    ... nsubj(likes-4, dog-2)
    ... advmod(likes-4, also-3)
    ... root(ROOT-0, likes-4)
    ... xcomp(likes-4, eating-5)
    ... dobj(eating-5, sausage-6)'''
    >>> tree = DepTree.fromstring(s)
    >>> print tree
    (dog-2, My-1)
    (likes-4, dog-2)
    (likes-4, also-3)
    (ROOT-0, likes-4)
    (likes-4, eating-5)
    (eating-5, sausage-6)
    """
    def __init__(self, token, children=[], parent=None, index=None):
        self.token = token
        self._children = children
        self._parent = parent
        self._index = index

    def is_root(self):
        return self._parent is None

    @property
    def index(self):
        if self.is_root():
            return None
        return self._index - 1

    def left(self):
        return [x for x in self.children if x.index < self.index]

    def right(self):
        return [x for x in self.children if x.index > self.index]

    @property
    def parent(self):
        return self.parent

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

    def __str__(self):
        pairs = list()
        for c in self.children:
            parent = "{0:s}-{1:d}".format(self.token, self._index)
            child = "{0:s}-{1:d}".format(c.token, c._index)
            pairs.append(parent + ', ' + child)
            pairs.append(self.__str__(c))
        return '\n'.join(pairs)

    @classmethod
    def fromstring(cls, s):
        leaves = dict()
        for line in s.strip().split('\n'):
            parent, child = line[line.find('(')+1: -1].split(', ')
            if parent not in leaves:
                parent_token, parent_index = parent.split('-')
                leaves[parent] = parent_node
                parent_node = cls(parent_token, index=int(parent_index))
            if child not in leaves:
                child_token, child_index = child.split('-')
                child_node = cls(child_token, index=int(child_index))
                leaves[child] = child_node
            leaves[parent].add_child(leaves[child])
        return leaves['ROOT-0']

if __name__ == '__main__':
    import doctest
    doctest.testmod()
