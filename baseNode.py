from . import parser


class BaseNode(object):

    def __init__(self, node):
        self.asc = node.asc
        self.index = node.index
        self.desc = node.desc
        self.size = node.size

        self.command, self.args = parser.tokenize_command(self.desc)
