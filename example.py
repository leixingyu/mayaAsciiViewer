import logging
import os
import sys
import time
from collections import OrderedDict

from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi
from guiUtil import prompt

from mayaAsciiParser import ascii, asciiData
from mayaAsciiParser.node import dagNode, dagModel


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(MODULE_PATH, 'mayaAsciiParser.ui')

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

p = r"C:\Users\Lei\Desktop\maya-example-scene\model\model-village-user-guide.ma"
p = r"C:\Users\Lei\Desktop\maya-example-scene\fx\PHX3_BeachWaves_Maya2015\PhoenixFD_Maya2015_BeachWaves.ma"
p = r"C:\Users\Lei\Desktop\maya-example-scene\rig\kayla_v1.9\kayla2017\kayla2017.ma"


class MyProxyModel(QtCore.QSortFilterProxyModel):
    """
    For configuring sorting and filtering
    """

    def __init__(self, *args, **kwargs):
        super(MyProxyModel, self).__init__(*args, **kwargs)

        # sorting
        self.setDynamicSortFilter(False)
        self.setSortRole(dagModel.DagModel.sort_role)
        self.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # filtering
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setFilterRole(dagModel.DagModel.filter_role)
        self.setFilterKeyColumn(0)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        _loadUi(UI_PATH, self)

        self._model = None
        self.proxy_model = MyProxyModel(self)

        self.ui_tree_view.setModel(self.proxy_model)
        self.ui_open_action.triggered.connect(self.load)

        self.ui_progress = QtWidgets.QProgressBar()
        self.statusBar().addPermanentWidget(self.ui_progress)

    def update_progress(self, value):
        self.ui_progress.setValue(value)

    def load(self):
        mfile = prompt.set_import_path(
            default_path=r"C:\Users\Lei\Desktop\maya-example-scene",
            file_type='*.ma'
        )

        if not mfile:
            return

        st = time.time()

        from mayaAsciiParser import loadThread
        progress_thread = loadThread.LoadThread()
        progress_thread.progressChanged.connect(self.update_progress)

        datas = [data for data in progress_thread.load(mfile)
                 if isinstance(data, asciiData.NodeData)]

        print 'time parsing file: {}'.format(time.time()-st)

        root = dagNode.from_ascii_data(datas)
        print 'time creating node: {}'.format(time.time()-st)

        self._model = dagModel.DagModel(root, self)
        self.proxy_model.setSourceModel(self._model)


def test():
    datas = asciiData.AsciiData.from_file(p)
    asc = ascii.Ascii(p)
    datas = sorted(datas, key=lambda n: n.size, reverse=1)
    datas = [asciiData.DataFactory(data) for data in datas]

    # size distribution
    create_size = 0
    connect_size = 0
    for data in datas:
        if isinstance(data, asciiData.NodeData):
            create_size += data.size

        elif isinstance(data, asciiData.ConnectionData):
            connect_size += data.size

    LOG.info('createNode size: %s; percent: %s%%', create_size,
             round(create_size/float(asc.size)*100, 2))
    LOG.info('connectAttr size: %skb; percent: %s%%', connect_size/1024,
             round(connect_size/float(asc.size)*100, 2))

    # createNode size distribution
    ntype = dict()
    for data in datas:
        if not isinstance(data, asciiData.NodeData):
            continue

        if data.dtype not in ntype.keys():
            ntype[data.dtype] = [data]
        else:
            ntype[data.dtype].append(data)

    # add size
    nsize = dict()
    for k, v in ntype.items():
        size = 0
        for data in v:
            size += data.size
        nsize[k] = size

    nsize = OrderedDict(sorted(nsize.items(), key=lambda kv: kv[1], reverse=True))

    result = ''
    for k, v in nsize.items()[:10]:
        result += "\t{} --- size: {}kb, percent: {}%\n".format(
                 k,
                 v/1024,
                 round(v/float(create_size) * 100, 3)
                 )
    LOG.info("top 10 most expensive create data:\n%s", result)


def show():
    global window
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show()
