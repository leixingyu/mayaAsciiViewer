"""

f = 'D:\\testbin\\maya-file.ma'
ma = MayaAscii(f)

with open("C:\Users\\Lei\\Downloads\\output.txt", "w") as file:
    file.write(ma.diagnose_usage())

"""


from collections import namedtuple

from . import ascii, parser


AsciiBase = namedtuple('AsciiBase', ['asc', 'index', 'desc', 'size'])


def diagnose_usage(path):
    output = ''

    # sort
    datas = AsciiData.from_file(path)
    datas = sorted(datas, key=lambda n: n.size, reverse=1)

    for data in datas:
        # filter
        if data.percent < 0.1:
            continue

        line = "[line: {index}][{size} mb][{percent}%] {description} \n".format(
            index=data.index,
            description=data.description,
            percent=data.percent,
            size=round(data.size / float(1024) / float(1024), 3)
        )
        output += line

    return output


def parse_data_by_type(path, ntype):
    """

    common data type: 'createNode' 'connectAttr'
    :param path:
    :param ntype:
    :return:
    """

    datas = AsciiData.from_file(path)
    return [data for data in datas if data.desc.startswith(ntype)]


class AsciiData(AsciiBase):
    __slots__ = ()

    def __new__(
        cls,
        asc,
        index,
        desc='',
        size=0
    ):
        return super(AsciiData, cls).__new__(cls, asc, index, desc, size)

    @classmethod
    def _from_file(cls, path):
        nodes = list()

        with open(path) as f:
            asc = ascii.Ascii(path)

            prv_index = -1
            prv_description = ''
            prv_size = 0

            for index, line in enumerate(f):
                if not line:
                    continue

                # a node doesn't have any indentation
                # whereas the node's attributes are all indented
                # the last node is ignored as it indicates end of file
                if not line.startswith('\t'):
                    node = cls(asc, prv_index, prv_description, prv_size)

                    prv_index = index + 1
                    prv_description = line
                    prv_size = len(line)

                    nodes.append(node)
                else:
                    prv_size += len(line)

        return nodes

    @classmethod
    def from_file(cls, path):
        nodes = list()
        asc = ascii.Ascii(path)

        with open(path) as f:

            # the first node
            index = 1
            line = f.readline()
            last_index = index
            last_line = line
            size = len(line)

            while True:
                # end of file
                if not line:
                    break

                # comment
                if line.startswith('//'):
                    pass

                # node has no indentation
                elif not line.startswith('\t'):
                    nodes.append(cls(asc, last_index, last_line, size))

                    size = len(line)
                    last_index = index

                    while not line.endswith(';\n'):
                        line += f.readline()
                        size += len(line)
                        index += 1

                    last_line = line

                else:
                    size += len(line)

                index += 1
                line = f.readline()

        return nodes

    @property
    def percent(self):
        percent = self.size / float(self.asc.size) * 100
        return round(percent, 3)


class DataFactory(object):

    def __new__(cls, data):
        command, _ = parser.tokenize_command(data.desc)

        args = [data.asc, data.index, data.desc, data.size]

        if command == 'createNode':
            return NodeData(*args)
        elif command == 'connectAttr':
            return ConnectionData(*args)


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


class NodeData(BaseData):
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


class ConnectionData(BaseData):

    def __init__(self, *args):
        super(ConnectionData, self).__init__(*args)

    @property
    def source(self):
        return self.args[0]

    @property
    def destination(self):
        return self.args[1]
