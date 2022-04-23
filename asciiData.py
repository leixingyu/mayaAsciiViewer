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


from pipelineUtil.fileSystem import winFile


class Ascii(winFile.WinFile):
    """
    Class for representing Maya Ascii file
    """

    def __init__(self, path):
        super(Ascii, self).__init__(path)
        if self.ext != '.ma':
            raise TypeError('File {} is not an Maya Ascii type'.format(self.path))

        self._lineCount = 0

    def update(self):
        super(Ascii, self).update()
        self.update_line()

    def update_line(self):
        with open(self._path) as f:
            for count, _line in enumerate(f):
                pass
            self._lineCount = count

    def read_detail(self, num):
        with open(self._path) as f:
            line = f.readline()
            count = 1
            is_start = False
            record_buf = ''

            while line:
                if is_start:
                    # reached next node
                    if not line.startswith('\t'):
                        break

                    record_buf += line

                if count == num:
                    if line.startswith('\t'):
                        break

                    is_start = True
                    record_buf += line

                count += 1
                line = f.readline()

        return record_buf


AsciiBase = namedtuple('AsciiBase', ['asc', 'index', 'desc', 'size', 'command', 'args'])


def new(ascii_node):
    command, args = tokenize_command(ascii_node.desc)
    args = [
        ascii_node.asc,
        ascii_node.index,
        ascii_node.desc,
        ascii_node.size,
        command,
        args
    ]

    if command == 'createNode':
        return NodeData(*args)
    else:
        return AsciiData(*args)


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


class AsciiData(AsciiBase):
    """
    An ascii string representation of an abstract node
    """

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

    @property
    def percent(self):
        percent = self.size / float(self.asc.size) * 100
        return round(percent, 3)


class NodeData(AsciiData):
    """
    An ascii string representation of a createNode mel command

    https://help.autodesk.com/cloudhelp/2018/ENU/Maya-Tech-Docs/CommandsPython/
    """

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


class ConnectionData(AsciiData):
    """
    An ascii string representation of a connectAttr mel command

    https://help.autodesk.com/cloudhelp/2018/ENU/Maya-Tech-Docs/CommandsPython/
    """

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


class FileData(AsciiData):

    def is_referenced(self):
        return '-r' in self.args

    def namespace(self):
        try:
            arg_ptr = self.args.index('-ns')
            return self.args[arg_ptr+1]
        except ValueError:
            return ''

    def reference_node(self):
        try:
            arg_ptr = self.args.index('-rfn')
            return self.args[arg_ptr+1]
        except ValueError:
            return ''

    def path(self):
        return self.args[-1]

