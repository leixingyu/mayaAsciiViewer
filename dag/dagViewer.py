import os
import sys


from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi
from guiUtil import prompt

from mayaAsciiParser import asciiData, loader
from mayaAsciiParser.dag import dagModel, builder


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(MODULE_PATH, 'dagViewer.ui')

p = r"C:\Users\Lei\Desktop\maya-example-scene\model\model-village-user-guide.ma"
# p = r"C:\Users\Lei\Desktop\maya-example-scene\fx\PHX3_BeachWaves_Maya2015\PhoenixFD_Maya2015_BeachWaves.ma"
p = r"C:\Users\Lei\Desktop\maya-example-scene\rig\kayla_v1.9\kayla2017\kayla2017.ma"


class PercentageDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super(PercentageDelegate, self).__init__(parent)

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


class MayaAsciiViewer(QtWidgets.QMainWindow):
    PERCENT_COLUMN = 3

    def __init__(self):
        super(MayaAsciiViewer, self).__init__()
        _loadUi(UI_PATH, self)

        self._model = None
        self.proxy_model = MyProxyModel(self)
        self.delegate = PercentageDelegate(self.ui_tree_view)

        self.ui_progress = QtWidgets.QProgressBar()

        self.config()
        self.connect_signals()

    def config(self):
        self.ui_progress.setVisible(False)
        self.statusBar().addPermanentWidget(self.ui_progress)

        self.ui_tree_view.setStyleSheet('QWidget{font: 10pt "Bahnschrift";}')
        self.ui_tree_view.setModel(self.proxy_model)
        self.ui_tree_view.setItemDelegateForColumn(self.PERCENT_COLUMN, self.delegate)

    def connect_signals(self):
        self.ui_tree_view.expanded.connect(self.make_children_persistent)

        self.ui_open_action.triggered.connect(lambda: self.load(p))
        self.ui_clear_action.triggered.connect(self.clear_view)

    def update_progress(self, value):
        self.ui_progress.setValue(value)

        if value >= 100:
            self.ui_progress.setVisible(False)
        elif self.ui_progress.isHidden():
            self.ui_progress.setVisible(True)

    def update_message(self, msg):
        self.statusBar().showMessage(msg, timeout=2)

    def load(self, mfile=None):
        mfile = get_ascii(mfile)
        if not mfile:
            return

        self.clear_view()
        self.load_view(mfile)
        self.format_view()

    def clear_view(self):
        # FIXME: this doesn't work correctly
        if self.ui_tree_view.model().sourceModel():
            # self._model = None
            # self.proxy_model.setSourceModel(self._model)
            self.ui_tree_view.model().sourceModel().clear()

    def format_view(self):
        self.ui_tree_view.header().resizeSection(0, 180)
        self.ui_tree_view.sortByColumn(self.PERCENT_COLUMN, QtCore.Qt.DescendingOrder)
        self.make_children_persistent()
        self.ui_tree_view.header().setStretchLastSection(1)

    def load_view(self, mfile=None):
        # file loading
        load_thread = loader.LoadThread()
        load_thread.progress_changed.connect(self.update_progress)
        load_thread.event_occurred.connect(self.update_message)

        datas = load_thread.load(mfile)

        # model building
        build_thread = builder.BuildThread()
        build_thread.progress_changed.connect(self.update_progress)
        build_thread.event_occurred.connect(self.update_message)

        node_datas = [asciiData.new(data) for data in datas
                      if isinstance(asciiData.new(data), asciiData.NodeData)]

        root = build_thread.build(node_datas)
        self._model = dagModel.DagModel(root, self)
        self.proxy_model.setSourceModel(self._model)

    def make_children_persistent(self, index=QtCore.QModelIndex()):
        for row in range(0, self.proxy_model.rowCount(index)):
            # no parent
            if index == QtCore.QModelIndex():
                child = self.proxy_model.index(row, self.PERCENT_COLUMN)

            # has parent
            else:
                child = index.child(row, self.PERCENT_COLUMN)

            self.ui_tree_view.openPersistentEditor(child)


def get_ascii(mfile=None):
    if not mfile:
        mfile = prompt.set_import_path(
            default_path=r"C:\Users\Lei\Desktop\maya-example-scene",
            file_type='*.ma'
        )

    if not mfile:
        prompt.message_log(ltype='error', message="Action Canceled by User")
        return

    if not os.path.exists(mfile):
        prompt.message_log(ltype='error', message="file not found \n{}".format(mfile))
        return

    return mfile


def show():
    global window
    app = QtWidgets.QApplication(sys.argv)
    window = MayaAsciiViewer()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show()
