import os
import sys
from collections import OrderedDict
from operator import itemgetter

from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi
from guiUtil import prompt
from guiUtil.template import pieChart
from pipelineUtil.data import palette


from mayaAsciiParser.data import audio, config, reference, requirement, info
from mayaAsciiParser import asciiData, loader
from mayaAsciiParser.dag import dagModel, builder


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(MODULE_PATH, 'asciiViewer.ui')

p = r"C:\Users\Lei\Desktop\maya-example-scene\model\model-village-user-guide.ma"
# p = r"C:\Users\Lei\Desktop\maya-example-scene\fx\PHX3_BeachWaves_Maya2015\PhoenixFD_Maya2015_BeachWaves.ma"
p = r"C:\Users\Lei\Desktop\maya-example-scene\rig\kayla_v1.9\kayla2017\kayla2017.ma"


class DockChart(QtWidgets.QDockWidget):

    def __init__(self, parent=None):
        super(DockChart, self).__init__(parent)

        self.chart = pieChart.SimpleChart()
        self.chart.resize(500, 300)
        chart_view = pieChart.SimpleChartView(self.chart)
        self.setWidget(chart_view)

    def set_datas(self, platte, datas, titles):
        s_datas = list()
        for i, item in enumerate(titles):
            data = pieChart.Data(item, datas[i], platte[i])
            s_datas.append(data)

        self.chart.set_series(s_datas)


class DockTable(QtWidgets.QDockWidget):
    def __init__(self, cls, parent=None):
        super(DockTable, self).__init__(parent)

        self.table = QtWidgets.QTableWidget()
        self.args = cls._fields

        self.table.setColumnCount(len(self.args))
        self.table.setHorizontalHeaderLabels(self.args)

        for i in range(self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.setWidget(self.table)

    def set_datas(self, datas):
        for data in datas:
            self.table.insertRow(self.table.rowCount())
            for i, arg in enumerate(self.args):
                self.table.setItem(self.table.rowCount()-1, i, QtWidgets.QTableWidgetItem(str(data[i])))


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
            color: '';
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


class AsciiViewer(QtWidgets.QMainWindow):
    PERCENT_COLUMN = 3

    def __init__(self):
        super(AsciiViewer, self).__init__()
        _loadUi(UI_PATH, self)

        self._model = None
        self.proxy_model = MyProxyModel(self)
        self.delegate = PercentageDelegate(self.ui_tree_view)

        self.ui_progress = QtWidgets.QProgressBar()

        self.config()

        self.chart = DockChart()
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.chart)

        self.smart_chart = DockChart()
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.smart_chart)

        self.info_table = DockTable(info.Info)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.info_table)

        self.req_table = DockTable(requirement.Requirement)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.req_table)

        self.conf_table = DockTable(config.Config)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.conf_table)

        self.ref_table = DockTable(reference.Reference)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.ref_table)

        self.audio_table = DockTable(audio.Audio)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.audio_table)

        self.connect_signals()

    def config(self):
        self.ui_progress.setVisible(False)
        self.statusBar().addPermanentWidget(self.ui_progress)

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
        self.statusBar().showMessage(msg, 2000)

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

        node_datas = [data for data in datas
                      if isinstance(data, asciiData.NodeData)]

        root = build_thread.build(node_datas)
        self._model = dagModel.DagModel(root, self)
        self.proxy_model.setSourceModel(self._model)

        self.set_datas(mfile)

    def make_children_persistent(self, index=QtCore.QModelIndex()):
        for row in range(0, self.proxy_model.rowCount(index)):
            # no parent
            if index == QtCore.QModelIndex():
                child = self.proxy_model.index(row, self.PERCENT_COLUMN)
            # has parent
            else:
                child = index.child(row, self.PERCENT_COLUMN)

            self.ui_tree_view.openPersistentEditor(child)

    def set_datas(self, path):
        datas = loader.LoadThread().load(path)

        # simple chart
        node = connection = other = 0
        for data in datas:
            if isinstance(data, asciiData.NodeData):
                node += data.size
            elif isinstance(data, asciiData.ConnectionData):
                connection += data.size
            else:
                other += data.size
        results = [node, connection, other]

        self.chart.set_datas(palette.PRIM_3, results, ['node', 'connection', 'other'])

        # smart chart
        root = self._model.get_node()
        items = get_distribution(root, top=10)
        self.smart_chart.set_datas(palette.TABLEAU_NEW_10, list(items.values()), list(items.keys()))

        infos = info.Info.from_datas(datas)
        self.info_table.set_datas(infos)

        reqs = requirement.Requirement.from_datas(datas)
        self.req_table.set_datas(reqs)

        conf = config.Config.from_datas(datas)
        self.conf_table.set_datas([conf])

        refs = reference.Reference.from_datas(datas)
        self.ref_table.set_datas(refs)

        audios = audio.Audio.from_datas(datas)
        self.audio_table.set_datas(audios)


def get_distribution(root, top=-1):
    nodes = get_children(root)

    typs = OrderedDict()
    for node in nodes:
        if node.typ not in typs:
            typs[node.typ] = node.size
        else:
            typs[node.typ] += node.size

    return OrderedDict(sorted(typs.items(), key=itemgetter(1), reverse=1)[0:top])


def get_children(root):
    nodes = list()
    for i in range(root.child_count):
        node = root.child(i)
        nodes.append(node)
        if node.child_count:
            nodes.extend(get_children(node))
    return nodes


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
    from qt_material import apply_stylesheet
    global window

    app = QtWidgets.QApplication(sys.argv)

    apply_stylesheet(app, theme='light_blue.xml')

    window = AsciiViewer()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    show()
