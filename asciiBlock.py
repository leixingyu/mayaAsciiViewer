from collections import namedtuple


AsciiBase = namedtuple('AsciiBase',
                       ['asc', 'index', 'desc', 'size', 'command', 'args'])


def get_distribution(blocks):
    node = connection = other = 0
    for block in blocks:
        if isinstance(block, NodeBlock):
            node += block.size
        elif isinstance(block, ConnectionBlock):
            connection += block.size
        else:
            other += block.size
    return [
        ('node', node),
        ('connection', connection),
        ('other', other)
    ]


class AsciiBlock(AsciiBase):
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
        return super(AsciiBlock, cls).__new__(cls, asc, index, desc, size, command, args)

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


class NodeBlock(AsciiBlock):
    """
    An ascii string representation of a createNode mel command

    https://help.autodesk.com/cloudhelp/2018/ENU/Maya-Tech-Docs/CommandsPython/
    """

    @property
    def typ(self):
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


class ConnectionBlock(AsciiBlock):
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
    def dest(self):
        """
        Destination attribute of the connected dependency

        :return: str. destination attribute name
        """
        return self.args[1]


class FileBlock(AsciiBlock):
    @property
    def is_ref(self):
        return '-r' in self.args

    @property
    def namespace(self):
        try:
            arg_ptr = self.args.index('-ns')
            return self.args[arg_ptr+1]
        except ValueError:
            return ''

    @property
    def ref_node(self):
        try:
            arg_ptr = self.args.index('-rfn')
            return self.args[arg_ptr+1]
        except ValueError:
            return ''

    @property
    def typ(self):
        try:
            arg_ptr = self.args.index('-typ')
            return self.args[arg_ptr+1]
        except ValueError:
            return ''

    @property
    def path(self):
        return self.args[-1]


class InfoBlock(AsciiBlock):
    @property
    def keyword(self):
        return self.args[0]

    @property
    def value(self):
        return self.args[1]


class RequirementBlock(AsciiBlock):
    @property
    def data_type(self):
        indices = [index for index, el in enumerate(self.args) if el == '-dataType']
        if not indices:
            return []
        return [self.args[index+1] for index in indices]

    @property
    def node_type(self):
        indices = [index for index, el in enumerate(self.args) if el == '-nodeType']
        if not indices:
            return []
        return [self.args[index+1] for index in indices]

    @property
    def product(self):
        return self.args[-2]

    @property
    def version(self):
        return self.args[-1]
