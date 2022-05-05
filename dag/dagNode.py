from collections import OrderedDict
from operator import itemgetter


def get_distribution(nodes, top=-1):
    typs = OrderedDict()
    for node in nodes:
        if node.typ not in typs:
            typs[node.typ] = node.size
        else:
            typs[node.typ] += node.size

    return sorted(typs.items(), key=itemgetter(1), reverse=True)[0:top]


def get_children(root):
    """
    Custom: get all nested children of the root

    :param root: DagNode. the root of the family tree
    :return: list of DagNodes. all nested children
             (children, grand-children, etc)
    """
    nodes = list()
    for i in range(root.child_count):
        node = root.child(i)
        nodes.append(node)
        if node.child_count:
            nodes.extend(get_children(node))
    return nodes


class DagNode(object):
    """
    Maya Dag node representation for hierarchical relationship
    """

    def __init__(self, name='', typ='', size=0, index=-1):
        """
        Initialization

        :param name: str. dag node name
        :param typ: str. dag node type
        :param size: int. dag node size in bytes
        """
        self.__name = name
        self.__typ = typ
        self.__size = size
        self.__index = index

        self.__parent = None
        self.__children = list()
        self.__total_size = size

    @property
    def name(self):
        return self.__name

    @property
    def typ(self):
        return self.__typ

    @property
    def size(self):
        return self.__size

    @property
    def index(self):
        return self.__index

    @property
    def parent(self):
        return self.__parent

    @property
    def row(self):
        """
        Index of the current node in relation to its parent's children,
        needed to support Qt Model View

        :return: int. children index of the current node from its parent
        """
        if self.__parent:
            return self.__parent.children.index(self)
        return 0

    @property
    def total_size(self):
        return self.__total_size

    @property
    def children(self):
        return self.__children

    @property
    def child_count(self):
        """
        Number of children

        :return: int. children count
        """
        return len(self.__children)

    def child(self, row):
        """
        Child of the current node on certain index
        needed to support Qt Model View

        :param row: int. index of the children
        :return: DagNode. child dag node
        """
        return self.__children[row]

    def append_child(self, child):
        self.__children.append(child)

    def set_parent(self, parent):
        """
        Set the parent of the current node, a node can only have one parent,
        a top level node is parented under scene root node, which is an
        invisible node.

        :param parent: DagNode. parent of the node
        """
        self.__parent = parent
        parent.append_child(self)
        parent.add_size(self.__size)

    def add_size(self, size):
        """
        Increase size of the current node, also propagate upwards to parents

        :param size: int. size in bytes
        """
        self.__total_size += size
        if self.__parent:
            self.__parent.add_size(size)
