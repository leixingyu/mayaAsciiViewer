from .. import asciiData


class DagNode(object):
    """
    Maya Dag node representation for hierarchical relationship
    """

    def __init__(self, name='', ntype='', size=0):
        """
        Initialization

        :param name: str. dag node name
        :param ntype: str. dag node type
        :param size: int. dag node size in bytes
        """
        self.name = name
        self.ntype = ntype
        self.size = size

        self.parent = None
        self.children = list()
        self.total_size = size

    @classmethod
    def from_data(cls, datas):
        """
        Create node networks from Ascii node data

        :param datas: list of NodeData(s). ascii data starting with 'createNode'
        :return: NodeData. root node data
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
        """
        Set the parent of the current node, a node can only have one parent,
        a top level node is parented under scene root node, which is an
        invisible node.

        :param parent: DagNode. parent of the node
        """
        self.parent = parent
        parent.children.append(self)
        parent.add_size(self.size)

    def add_size(self, size):
        """
        Increase size of the current node, also propagate upwards to parents

        :param size: int. size in bytes
        """
        self.total_size += size
        if self.parent:
            self.parent.add_size(size)

    def row(self):
        """
        Index of the current node in relation to its parent's children,
        needed to support Qt Model View

        :return: int. children index of the current node from its parent
        """
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def child(self, row):
        """
        Child of the current node on certain index
        needed to support Qt Model View

        :param row: int. index of the children
        :return: DagNode. child dag node
        """
        return self.children[row]

    @property
    def child_count(self):
        """
        Number of children

        :return: int. children count
        """
        return len(self.children)
