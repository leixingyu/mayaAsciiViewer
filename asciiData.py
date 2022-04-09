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


AsciiBase = namedtuple('AsciiBase', ['asc', 'index', 'desc', 'size', 'command', 'args'])


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
