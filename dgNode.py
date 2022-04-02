from . import nodeData


class DGNode(object):
    """
    An actual directed graph (hierarchical) node representation
    """

    def __init__(self):
        self._name = ''
        self._ntype = ''
        self._size = 0
        self._parent = None
        self._children = list()

        self._total_size = 0

    @classmethod
    def create_root(cls):
        return cls()

    @classmethod
    def from_nodes(cls, datas):
        """

        :param datas: list of NodeData(s).
        :return:
        """
        root_node = cls()

        nodes = list()
        for i, data in enumerate(datas):
            if not isinstance(data, nodeData.NodeData):
                raise TypeError

            node = cls()
            nodes.append(node)
            node.name = data.name
            node.ntype = data.dtype
            node.size = data.size
            node._total_size = node.size

            if data.parent:
                while i >= 0:
                    if datas[i-1].name == data.parent:
                        node.set_parent(nodes[i-1])
                        break
                    i -= 1
            else:
                node.set_parent(root_node)

        return root_node

    def set_parent(self, parent):
        self._parent = parent
        parent.append_child(self)

    def append_child(self, child):
        self.children.append(child)
        self.update_total_size()
        if self.parent:
            self.parent.update_total_size()

    def update_total_size(self):
        self._total_size = self.size
        for child in self.children:
            self._total_size += child.total_size

    @property
    def total_size(self):
        return self._total_size

    def insert_child(self, row, child):
        if row < 0 or row > len(self.children):
            return False

        self._children.insert(row, child)
        child.set_parent(self)
        return True

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def child(self, row):
        return self._children[row]

    @property
    def child_count(self):
        return len(self._children)

    @property
    def ntype(self):
        return self._ntype

    @ntype.setter
    def ntype(self, ntype):
        self._ntype = ntype

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

