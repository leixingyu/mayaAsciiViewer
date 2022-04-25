import logging
import sys

from Qt import QtCore, QtWidgets, QtGui
from PyQt5 import QtChart

from mayaAsciiParser import asciiData, loader
from mayaAsciiParser.data import audio, config, reference, requirement

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def search(path):
    load_thread = loader.LoadThread()
    datas = load_thread.load(path)

    audios = audio.Audio.from_datas(datas)
    for au in audios:
        print(au._asdict())

    conf = config.Config.from_datas(datas)
    print(conf._asdict())

    refs = reference.Reference.from_datas(datas)
    for ref in refs:
        print(ref._asdict())

    reqs = requirement.Requirement.from_datas(datas)
    for req in reqs:
        print(req._asdict())


def parse(path):
    load_thread = loader.LoadThread()
    datas = load_thread.load(path)

    # size distribution
    create_size = 0
    connect_size = 0

    for data in datas:
        if isinstance(data, asciiData.NodeData):
            create_size += data.size

        elif isinstance(data, asciiData.ConnectionData):
            connect_size += data.size


if __name__ == '__main__':
    global win
    app = QtWidgets.QApplication(sys.argv)
    win = Chart()
    win.show()
    sys.exit(app.exec_())
    # search(r"C:\Users\Lei\Desktop\test.ma")
    # parse(r"C:\Users\Lei\Desktop\test.ma")
