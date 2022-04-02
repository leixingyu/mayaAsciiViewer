from . import parser


class BaseData(object):

    def __init__(self, asc, index, desc, size):
        self._asc = asc
        self._index = index
        self._desc = desc
        self._size = size

        self._command, self._args = parser.tokenize_command(self.desc)

    @property
    def asc(self):
        return self._asc

    @property
    def index(self):
        return self._index

    @property
    def desc(self):
        return self._desc

    @property
    def size(self):
        return self._size

    @property
    def command(self):
        return self._command

    @property
    def args(self):
        return self._args
