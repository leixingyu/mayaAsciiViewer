
from . import parser

from . import createNode
from . import connectNode


class NodeFactory(object):

    def __new__(cls, node):
        command, _ = parser.tokenize_command(node.desc)
        if command == 'createNode':
            return createNode.CreateNode(node)
        elif command == 'connectAttr':
            return connectNode.ConnectNode(node)

