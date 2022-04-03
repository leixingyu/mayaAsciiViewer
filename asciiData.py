"""

f = 'D:\\testbin\\maya-file.ma'
ma = MayaAscii(f)

with open("C:\Users\\Lei\\Downloads\\output.txt", "w") as file:
    file.write(ma.diagnose_usage())

"""


from collections import namedtuple

from . import ascii


AsciiBase = namedtuple('AsciiBase', ['asc', 'index', 'desc', 'size', 'command', 'args'])


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
        size=0,
        command='',
        args=None
    ):
        return super(AsciiData, cls).__new__(cls, asc, index, desc, size, command, args)

    @classmethod
    def from_file(cls, path):
        """
        57% faster than .readline()

        :param path:
        :return:
        """

        nodes = list()

        with open(path) as f:
            asc = ascii.Ascii(path)
            buf_index = -1
            buf_desc = ''
            buf_size = 0

            for index, line in enumerate(f):
                # empty line
                if not line:
                    continue

                # comment
                if line.startswith('\\'):
                    continue

                # node
                if not line.startswith('\t'):
                    nodes.append(cls(asc, buf_index, buf_desc, buf_size))
                    buf_index = index + 1
                    buf_size = len(line)
                    buf_desc = line

                    is_open = True
                else:
                    if is_open:
                        buf_desc += line
                    buf_size += len(line)

                if is_open and line.endswith(';\n'):
                    is_open = False

        return nodes

    @classmethod
    def _from_file(cls, path):
        """
        Obsolete; slower to parse the ascii file
        Could be use to cross-validate parsed data

        :param path:
        :return:
        """

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
        command, args = DataFactory.tokenize_command(data.desc)

        args = [data.asc, data.index, data.desc, data.size, command, args]

        if command == 'createNode':
            return NodeData(*args)
        elif command == 'connectAttr':
            return ConnectionData(*args)

    @staticmethod
    def tokenize_command(line):
        """

        Source: https://github.com/mottosso/maya-scenefile-parser/

        :param line: str
        :return:
        """
        command, _, line = line.partition(" ")
        command = command.lstrip()

        args = list()
        while True:
            line = line.strip()

            if not line:
                break

            # handle quotation marks in string
            if line[0] in ['\"', "\'"]:
                string_delim = line[0]
                escaped = False
                string_end = len(line)

                # find the closing quote as string end
                for i in range(1, len(line)):
                    if not escaped and line[i] == string_delim:
                        string_end = i
                        break
                    elif not escaped and line[i] == "\\":
                        escaped = True
                    else:
                        escaped = False

                arg, line = line[1:string_end], line[string_end+1:]

            else:
                arg, _, line = line.partition(" ")

            args.append(arg)

        return command, args


class NodeData(AsciiBase):
    """
    A node representation based off an ascii string
    """
    __slots__ = ()

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


class ConnectionData(AsciiBase):
    __slots__ = ()

    @property
    def source(self):
        return self.args[0]

    @property
    def destination(self):
        return self.args[1]
