"""
Module to perform maya ascii file loading

Example
```python
loader = Loader()
blocks = loader.load(mfile)
```

`progress_changed` signal can be connected to progress bar to reflect load
progress and `event_occurred` can be connected to status bar to display
event message
"""

import math
import time

from Qt import QtCore
from pipelineUtil.fileSystem import fp

from . import asciiBlock


def new(asc, index, desc, size):
    """
    Factor function to create different sub-types of AsciiBlock instances

    :param asc: Ascii. the ascii file responsible for the data block
    :param index: int. the starting line number of the block
    :param desc: str. the starting line describing the block
    :param size: int. the entire size in byte of the data block
    :return: AsciiBlock. an instance of a sub-type of AsciiBlock
    """
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
        return asciiBlock.NodeBlock(*args)
    elif command == 'connectAttr':
        return asciiBlock.ConnectionBlock(*args)
    elif command == 'file':
        return asciiBlock.FileBlock(*args)
    elif command == 'requires':
        return asciiBlock.RequirementBlock(*args)
    elif command == 'fileInfo':
        return asciiBlock.InfoBlock(*args)
    else:
        return asciiBlock.AsciiBlock(*args)


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


class Loader(QtCore.QObject):
    """
    Loader for ascii data blocks
    this should be the standard way of loading ascii file into individual
    data blocks
    """
    progress_changed = QtCore.Signal(int)
    event_occurred = QtCore.Signal(str)

    def load(self, path):
        """
        Create a network of Ascii blocks from a path

        57% faster than .readline()

        :param path: str. .ma full path
        :return: list of AsciiData. data network
        """
        start_time = time.time()
        self.event_occurred.emit('Reading File')
        blocks = list()

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
                    block = new(asc, buf_index, buf_desc, buf_size)
                    blocks.append(block)

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
        return blocks


class Ascii(fp.File):
    """
    Class for representing Maya Ascii file
    """
    def __init__(self, path):
        """
        Initialization

        :param path: str. path to maya ascii file
        """
        super(Ascii, self).__init__(path)
        if self.ext != '.ma':
            raise TypeError('File {} is not an Maya Ascii type'.format(self.path))

        self._lineCount = 0

    def update(self):
        """
        Override. update file related attribute
        """
        super(Ascii, self).update()
        self.update_line()

    def update_line(self):
        """
        Update ascii file line count
        """
        with open(self._path) as f:
            for count, _line in enumerate(f):
                pass
            self._lineCount = count

    def read_detail(self, num):
        """
        Read the full detail description of an ascii block

        Full description includes all sub-information of the block rather than
        just the top level description. since it is time-consuming and memory
        demanding to store, this function is called on demand.

        Example:
        createNode transform -s -n "persp";
            rename -uid "F1591FE8-416B-F4AE-B3B8-9C923044C14D";
            setAttr ".v" no;
            setAttr ".t" -type "double3" -319.18663032960933 136.34364156607776 410.86015622114041 ;
            setAttr ".r" -type "double3" -4.5383530389700519 -400.60000000010535 2.6180979798846528e-16 ;
            setAttr ".rp" -type "double3" -3.5527136788005009e-15 -2.8421709430404007e-14 5.6843418860808015e-14 ;
            setAttr ".rpt" -type "double3" -6.6120476298659498e-14 -3.0659371400595595e-12 -2.0398895670677526e-12 ;

        :param num: int. line number
        :return: str. full description of the ascii block
        """
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
