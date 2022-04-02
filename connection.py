from . import baseData


class Connection(baseData.BaseData):

    def __init__(self, *args):
        super(Connection, self).__init__(*args)

    @property
    def source(self):
        return self.args[0]

    @property
    def destination(self):
        return self.args[1]
