
from . import parser

from . import nodeData
from . import connection


class DataFactory(object):

    def __new__(cls, data):
        command, _ = parser.tokenize_command(data.desc)

        args = [data.asc, data.index, data.desc, data.size]

        if command == 'createNode':
            return nodeData.NodeData(*args)
        elif command == 'connectAttr':
            return connection.Connection(*args)

