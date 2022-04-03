"""
Example Use:

f = 'D:\\testbin\\maya-file.ma'

# get only create nodes
datas = AsciiData.from_file(path)
createNodes = [data for data in datas if data.desc.startswith('createNode')]

# output a rough diagnose

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
print(output)
"""


from collections import namedtuple

from . import ascii


AsciiBase = namedtuple('AsciiBase', ['asc', 'index', 'desc', 'size', 'command', 'args'])


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
        """
        Initialization

        Example:
        createNode transform -s -n "persp";
            rename -uid "BE01090D-497F-9171-93CC-2491F449EA81";
            setAttr ".v" no;
            setAttr ".t" -type "double3" 9.3387705225703108 20.24908436997945 13.862604897356242 ;
            setAttr ".r" -type "double3" -18.93835092203701 381.79999999915066 0 ;
            setAttr ".rp" -type "double3" 0 -2.2204460492503131e-16 -1.7763568394002505e-15 ;
            setAttr ".rpt" -type "double3" -3.4079865368345278e-15 -1.0306446117598169e-16 2.2620589140777267e-15 ;

        :param asc: ascii.Ascii. the ascii file associated with the data,
        the data is meaningless without seeing from the scope of the file level
        :param index: int. the start line number of the current data
        :param desc: str. parent mel command (i.e. first line of a series
        of mel commands: createNode transform -s -n "persp";)
        :param size: int. size of the full mel commands data in bytes
        :param command: str. parent mel command's name (i.e. createNode)
        :param args: list. parent mel command's arguments (i.e. [transform,
        -s, -n, "persp"])
        """
        return super(AsciiData, cls).__new__(cls, asc, index, desc, size, command, args)

    def __str__(self):
        return '{}({}, {}, {})'.format(
            self.__class__.__name__,
            self.index,
            self.desc,
            self.size,
        )

    @classmethod
    def from_file(cls, path):
        """
        Create a network of Ascii datas from a path

        57% faster than .readline()

        :param path: str. .ma full path
        :return: list of AsciiData. data network
        """
        datas = list()
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
                    datas.append(cls(asc, buf_index, buf_desc, buf_size))
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

        return datas

    @classmethod
    def _from_file(cls, path):
        """
        Obsolete; slower alternative to parse the ascii file
        Could be use to cross-validate parsed data
        """
        datas = list()
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
                    datas.append(cls(asc, last_index, last_line, size))

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

        return datas

    @property
    def percent(self):
        percent = self.size / float(self.asc.size) * 100
        return round(percent, 3)


class DataFactory(object):
    """
    Factory for creating sub data types based on AsciiData
    """
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
        Tokenize mel command into list of arguments for easier processing
        Source: https://github.com/mottosso/maya-scenefile-parser/

        :param line: str. mel command
        :return: tuple (str, list). command name, and list of arguments
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
    An ascii string representation of a createNode mel command

    https://help.autodesk.com/cloudhelp/2018/ENU/Maya-Tech-Docs/CommandsPython/
    """

    __slots__ = ()

    @property
    def dtype(self):
        """
        Type of the node created (e.g. "transform", "camera", "nurbsSurface")

        :return: str. node type
        """
        return self.args[0]

    @property
    def name(self):
        """
        Name of the node created

        :return: str. node name
        """
        try:
            arg_ptr = self.args.index('-n')
            return self.args[arg_ptr+1]
        except ValueError:
            return ''

    @property
    def parent(self):
        """
        Parent in the Dag under which the new node belongs

        :return: str. name of the parent node
        """
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
    """
    An ascii string representation of a connectAttr mel command

    https://help.autodesk.com/cloudhelp/2018/ENU/Maya-Tech-Docs/CommandsPython/
    """

    __slots__ = ()

    @property
    def source(self):
        """
        Source attribute of the connected dependency

        :return: str. source attribute name
        """
        return self.args[0]

    @property
    def destination(self):
        """
        Destination attribute of the connected dependency

        :return: str. destination attribute name
        """
        return self.args[1]
