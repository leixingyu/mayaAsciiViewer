from collections import namedtuple

from . import ascii


AsciiBase = namedtuple('AsciiBase', ['asc', 'index', 'desc', 'size'])


class AsciiNode(AsciiBase):
    __slots__ = ()

    def __new__(
        cls,
        asc,
        index,
        desc='',
        size=0
    ):
        return super(AsciiNode, cls).__new__(cls, asc, index, desc, size)

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
