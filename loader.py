import math
import time

from Qt import QtCore
from pipelineUtil.fileSystem import winFile

from . import asciiData


def new(asc, index, desc, size):
    command, args = tokenize_command(desc)
    args = [
        asc,
        index,
        desc,
        size,
        command,
        args
    ]

    if command == 'createNode':
        return asciiData.NodeData(*args)
    elif command == 'connectAttr':
        return asciiData.ConnectionData(*args)
    elif command == 'file':
        return asciiData.FileData(*args)
    elif command == 'requires':
        return asciiData.RequirementData(*args)
    elif command == 'fileInfo':
        return asciiData.InfoData(*args)
    else:
        return asciiData.AsciiData(*args)


def tokenize_command(line):
    """
    Tokenize mel command into list of arguments for easier processing
    Source: https://github.com/mottosso/maya-scenefile-parser/

    :param line: str. mel command
    :return: tuple (str, list). command name, and list of arguments
    """
    command, _, line = line.partition(" ")
    command = command.lstrip()
    line = line[:-2]  # remove the trailing ;

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
            asc = Ascii(path)
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
                    data = new(asc, buf_index, buf_desc, buf_size)
                    datas.append(data)

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
