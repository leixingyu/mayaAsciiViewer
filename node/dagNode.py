from .. import asciiData


class DagNode(object):
    """
    An actual directed graph (hierarchical) node representation
    """

    def __init__(self, name='', ntype='', size=0):
        self.name = name
        self.ntype = ntype
        self.size = size
        self.parent = None
        self.children = list()

        self.total_size = size

    @classmethod
    def from_nodes(cls, datas):
        """

        :param datas: list of NodeData(s).
        :return:
        """
        root_node = cls()

        nodes = list()
        for i, data in enumerate(datas):
            if not isinstance(data, asciiData.NodeData):
                raise TypeError

            node = cls(data.name, data.dtype, data.size)
            nodes.append(node)

            parent = None
            if data.parent:
                while i > 0:
                    i -= 1
                    # sometimes the name contains '|'
                    if data.parent.endswith(datas[i].name):
                        parent = nodes[i]
                        break

                if not parent:
                    raise ValueError(
                        'Parent {} not found'.format(data.parent)
                    )

            else:
                parent = root_node

            node.set_parent(parent)

        return root_node

    def set_parent(self, parent):
        self.parent = parent
        parent.children.append(self)
        parent.add_size(self.size)

    def add_size(self, size):
        self.total_size += size
        if self.parent:
            self.parent.add_size(size)

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def child(self, row):
        return self.children[row]

    @property
    def child_count(self):
        return len(self.children)
