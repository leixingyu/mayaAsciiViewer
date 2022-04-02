import logging
import time
import sys
from collections import OrderedDict

from Qt import QtWidgets, QtCore, QtGui

from mayaAsciiParser import asciiData, ascii
from mayaAsciiParser.node import dagNode, dagModel, view

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()

        self.setCentralWidget(widget)
        widget.setLayout(layout)

        self.ui_tree_view = view.View()
        # self.ui_tree_view.setStyleSheet('QWidget{font: 10pt "Bahnschrift";}')

        layout.addWidget(self.ui_tree_view, 1, 0)

        p = r"C:\Users\Lei\Downloads\main2.ma"

        # initialize datas
        datas = asciiData.AsciiData.from_file(p)
        datas = [asciiData.DataFactory(data) for data in datas]

        datas = [data for data in datas if isinstance(data, asciiData.NodeData)]

        root = dagNode.DagNode.from_nodes(datas)
        print root.total_size
        self._model = dagModel.DagModel(root, self)

        # proxy model
        self._proxyModel = QtCore.QSortFilterProxyModel(self)
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(False)
        self._proxyModel.setSortRole(dagModel.DagModel.sortRole)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._proxyModel.setFilterRole(dagModel.DagModel.filterRole)
        self._proxyModel.setFilterKeyColumn(0)

        self.ui_tree_view.setModel(self._proxyModel)


def show():
    st = time.time()
    global window
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    print time.time() - st
    sys.exit(app.exec_())


if __name__ == '__main__':
    show()


def test2():
    st = time.time()
    p = r"C:\Users\Lei\Downloads\main2.ma"

    # initialize datas
    datas = asciiData.AsciiData.from_file(p)
    datas = [asciiData.DataFactory(data) for data in datas]

    datas = [data for data in datas if isinstance(data, asciiData.NodeData)]
    print len(datas)
    print time.time() - st

    root = dagNode.DagNode.from_nodes(datas)

    for node in root.children:
        print node.name
        for child in node.children:
            print '\t' + child.name

    print time.time() - st


def ex1():
    p = r"C:\Users\Lei\Desktop\test.ma"

    # initialize datas
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

    LOG.info('createNode size: %skb; percent: %s%%',
             create_size/1024,
             round(create_size/float(asc.size)*100, 2)
             )
    LOG.info('connectAttr size: %skb; percent: %s%%',
             connect_size/1024,
             round(connect_size/float(asc.size)*100, 2)
             )

    # createNode size distribution

    # group by type
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
