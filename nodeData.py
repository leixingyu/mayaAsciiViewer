from . import baseData


class NodeData(baseData.BaseData):
    """
    A node representation based off an ascii string
    """

    def __init__(self, *args):
        super(NodeData, self).__init__(*args)
        if self.command != 'createNode':
            raise ValueError

    @property
    def dtype(self):
        return self.args[0]

    @property
    def name(self):
        try:
            arg_ptr = self.args.index('-n')
            return self.args[arg_ptr+1]
        except ValueError:
            return ''

    @property
    def parent(self):
        try:
            arg_ptr = self.args.index('-p')
            return self.args[arg_ptr+1]
        except ValueError:
            return ''

    @property
    def is_shared(self):
        return '-s' in self.args

    @property
    def is_skiped(self):
        return '-ss' in self.args
