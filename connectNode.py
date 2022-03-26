from . import baseNode


class ConnectNode(baseNode.BaseNode):

    def __init__(self, node):
        super(ConnectNode, self).__init__(node)

        if self.command != 'connectAttr':
            raise ValueError

    @property
    def source(self):
        return self.args[0]

    @property
    def destination(self):
        return self.args[1]
