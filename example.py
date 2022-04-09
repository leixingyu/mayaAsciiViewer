import logging
import os
import sys
import time
from collections import OrderedDict

from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi
from guiUtil import prompt

from mayaAsciiParser import ascii, asciiData, loadThread
from mayaAsciiParser.node import dagNode, dagModel


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(MODULE_PATH, 'mayaAsciiParser.ui')

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

p = r"C:\Users\Lei\Desktop\maya-example-scene\model\model-village-user-guide.ma"
# p = r"C:\Users\Lei\Desktop\maya-example-scene\fx\PHX3_BeachWaves_Maya2015\PhoenixFD_Maya2015_BeachWaves.ma"
p = r"C:\Users\Lei\Desktop\maya-example-scene\rig\kayla_v1.9\kayla2017\kayla2017.ma"


class Delegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super(Delegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QProgressBar(parent)
        editor.setMinimum(0)
        editor.setMaximum(100)

        return editor

    def setEditorData(self, editor, index):
        model_value = index.model().data(index, QtCore.Qt.EditRole)
        GRADS = ['#c0ff33', '#feff5c', '#ffc163', '#ffa879', '#fb4b4b', '#fb4b4b']
        color = GRADS[int(model_value / 20)]

        style = """
        QProgressBar {{
            border: 1px solid grey;
            text-align: center;
        }}

        QProgressBar::chunk {{
            background-color: {};
        }}
        """.format(color)

        editor.setValue(model_value)
        editor.setStyleSheet(style)


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
    PERCENT_COLUMN = 3

    def __init__(self):
        super(MainWindow, self).__init__()
        _loadUi(UI_PATH, self)

        self._model = None
        self.proxy_model = MyProxyModel(self)
        delegate = Delegate(self.ui_tree_view)

        self.ui_tree_view.setModel(self.proxy_model)
        self.ui_tree_view.setItemDelegateForColumn(MainWindow.PERCENT_COLUMN, delegate)
        self.ui_tree_view.expanded.connect(self.makeChildrenPersistent)
        self.ui_tree_view.setStyleSheet('QWidget{font: 10pt "Bahnschrift";}')

        self.ui_open_action.triggered.connect(lambda: self.load(p))

        self.ui_progress = QtWidgets.QProgressBar()
        self.statusBar().addPermanentWidget(self.ui_progress)

    def update_progress(self, value):
        self.ui_progress.setValue(value)

    def load(self, mfile=None):
        if not mfile:
            mfile = prompt.set_import_path(
                default_path=r"C:\Users\Lei\Desktop\maya-example-scene",
                file_type='*.ma'
            )

        if not mfile:
            prompt.message_log(ltype='error', message="Action Canceled by User")
            return

        st = time.time()

        progress_thread = loadThread.LoadThread()
        progress_thread.progressChanged.connect(self.update_progress)

        def get_root(mfile):
            datas = [data for data in progress_thread.load(mfile)
                     if isinstance(data, asciiData.NodeData)]

            print 'time parsing file: {}'.format(time.time()-st)

            root = dagNode.from_ascii_data(datas)
            print 'time creating node: {}'.format(time.time()-st)
            return root

        self._model = dagModel.DagModel(get_root(mfile), self)
        self.proxy_model.setSourceModel(self._model)

        self.ui_tree_view.sortByColumn(MainWindow.PERCENT_COLUMN)

        self.makeChildrenPersistent()

    def visibleRange(self):
        top = self.ui_tree_view.viewport().rect().topLeft()
        bottom = self.ui_tree_view.viewport().rect().bottomLeft()
        return range(self.ui_tree_view.indexAt(top).row(),
                     self.ui_tree_view.indexAt(bottom).row()+1)

    def makeChildrenPersistent(self, index=QtCore.QModelIndex()):
        for row in range(0, self.proxy_model.rowCount(index)):
            # no parent
            if index == QtCore.QModelIndex():
                child = self.proxy_model.index(row, MainWindow.PERCENT_COLUMN)

            # has parent
            else:
                child = index.child(row, MainWindow.PERCENT_COLUMN)

            self.ui_tree_view.openPersistentEditor(child)


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
