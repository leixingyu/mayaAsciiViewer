import math
import time

from Qt import QtCore

from . import asciiData


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
            asc = asciiData.Ascii(path)
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
                    datas.append(asciiData.AsciiData(asc, buf_index, buf_desc, buf_size))

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
