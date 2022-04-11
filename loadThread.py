import math
import time

from Qt import QtCore

from . import ascii, asciiData
from .node import dagNode


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


def new(asc, buf_index, buf_desc, buf_size):
    command, args = tokenize_command(buf_desc)
    args = [asc, buf_index, buf_desc, buf_size, command, args]
    if command == 'createNode':
        return asciiData.NodeData(*args)
    elif command == 'connectAttr':
        return asciiData.ConnectionData(*args)
    else:
        return asciiData.AsciiData(*args)


class LoadThread(QtCore.QThread):
    progress_changed = QtCore.Signal(int)
    event_occurred = QtCore.Signal(str)

    def load(self, path):
        """
        Create a network of Ascii datas from a path

        57% faster than .readline()

        :param path: str. .ma full path
        :return: list of AsciiData. data network
        """
        start_time = time.time()
        self.event_occurred.emit('Reading File')
        datas = list()

        with open(path) as f:
            asc = ascii.Ascii(path)
            total_size = float(asc.size)
            buf_index = -1
            buf_desc = ''
            buf_size = 0

            cache_size = 0  # total file size read into cache
            for index, line in enumerate(f):
                # empty line
                if not line:
                    continue

                # comment
                if line.startswith('\\'):
                    continue

                # new node happens when lines aren't indented
                if not line.startswith('\t'):
                    # create node based on previous buffer
                    datas.append(new(asc, buf_index, buf_desc, buf_size))

                    # update load status
                    cache_size += buf_size
                    progress = int(math.ceil(cache_size / total_size * 100))
                    self.progress_changed.emit(progress)

                    # store the current node into buffer
                    buf_index = index+1
                    buf_size = len(line)
                    buf_desc = line

                    is_open = True
                else:
                    if is_open:
                        buf_desc += line
                    buf_size += len(line)

                # handling multi-line nodes
                if is_open and line.endswith(';\n'):
                    is_open = False

        time_elapsed = round(time.time() - start_time, 3)
        self.event_occurred.emit('File Load Complete: {}s'.format(time_elapsed))

        return datas

    def build(self, datas):
        """
        Create node networks from Ascii datas

        :param datas: list of NodeData(s). ascii data starting with 'createNode'
        :return: NodeData. root node data
        """
        start_time = time.time()
        self.event_occurred.emit('Building DAG Tree')
        root_node = dagNode.DagNode()
        nodes = list()

        for i, data in enumerate(datas):
            if not isinstance(data, asciiData.NodeData):
                raise TypeError

            node = dagNode.DagNode(data.name, data.dtype, data.size, data.index)
            nodes.append(node)
            self.progress_changed.emit(int(float(len(nodes)) / len(datas) * 100))

            parent = None
            if data.parent:
                while i > 0:
                    i -= 1
                    # sometimes the name contains '|'
                    if data.parent.endswith(datas[i].name):
                        parent = nodes[i]
                        break

                if not parent:
                    raise ValueError(
                        'Parent {} not found'.format(data.parent)
                    )
            else:
                parent = root_node

            node.set_parent(parent)

        time_elapsed = round(time.time() - start_time, 3)
        self.event_occurred.emit('Build Complete: {}s'.format(time_elapsed))

        return root_node
