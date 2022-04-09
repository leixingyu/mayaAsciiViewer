from Qt import QtCore

from . import ascii, asciiData


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
    progressChanged = QtCore.Signal(int)

    def load(self, path):
        """
        Create a network of Ascii datas from a path

        57% faster than .readline()

        :param path: str. .ma full path
        :return: list of AsciiData. data network
        """
        datas = list()
        with open(path) as f:
            asc = ascii.Ascii(path)
            total_size = float(asc.size)
            buf_index = -1
            buf_desc = ''
            buf_size = 0

            cache_size = 0
            for index, line in enumerate(f):
                # empty line
                if not line:
                    continue

                # comment
                if line.startswith('\\'):
                    continue

                # node
                if not line.startswith('\t'):
                    node = new(asc, buf_index, buf_desc, buf_size)

                    datas.append(node)
                    cache_size += buf_size
                    progress = int(cache_size / total_size * 100)
                    self.progressChanged.emit(progress)

                    buf_index = index+1
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
