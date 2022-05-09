import os
import sys

from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi
from guiUtil.template import pieChart, table
from pipelineUtil.data import palette

from mayaAsciiParser import asciiBlock, asciiLoader
from mayaAsciiParser.block import audio, config, reference, requirement, info
from mayaAsciiParser.dag import dagBuilder, dagView, dagNode


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(MODULE_PATH, 'asciiViewer.ui')
ICON_PATH = os.path.join(MODULE_PATH, 'icon.png')
PROJECT_DIR = os.path.expandvars("%USERPROFILE%\\Desktop")


class DockChart(QtWidgets.QDockWidget):

    def __init__(self, parent):
        super(DockChart, self).__init__(parent)
        self.__parent = parent

        self.__chart = pieChart.SimpleChart()
        self.__chart.resize(500, 300)

        chart_view = pieChart.SimpleChartView(self.__chart)
        self.setWidget(chart_view)

        self.dock()

    def dock(self, position=QtCore.Qt.RightDockWidgetArea):
        self.__parent.addDockWidget(position, self)

    def reset(self):
        if self.isFloating():
            self.setFloating(False)
        if not self.isVisible():
            self.setVisible(True)
        self.dock()

    def add_slice(self, name, value, color):
        self.__chart.add_slice(name, value, color)

    def clear(self):
        self.reset()
        self.__chart.clear()


class DockTable(QtWidgets.QDockWidget):
    def __init__(self, cls, parent):
        super(DockTable, self).__init__(parent)
        self.setWindowTitle(cls.__name__)

        self.__parent = parent

        self.__args = cls._fields
        self.__table = table.SmartTable()
        self.__table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.__table.setColumnCount(len(self.__args))
        self.__table.setHorizontalHeaderLabels(
            [label.replace('_', ' ') for label in self.__args]
        )

        self.setWidget(self.__table)
        self.dock()

    def dock(self, position=QtCore.Qt.LeftDockWidgetArea):
        self.__parent.addDockWidget(position, self)

    def reset(self):
        if self.isFloating():
            self.setFloating(False)
        if not self.isVisible():
            self.setVisible(True)
        self.dock()

    def add_entry(self, values):
        self.__table.insertRow(self.__table.rowCount())
        for i, arg in enumerate(self.__args):
            self.__table.setItem(
                self.__table.rowCount()-1,
                i,
                QtWidgets.QTableWidgetItem(str(values[i]))
            )

    def clear(self):
        self.reset()
        self.__table.setRowCount(0)


class AsciiViewer(QtWidgets.QMainWindow):

    def __init__(self):
        super(AsciiViewer, self).__init__()
        _loadUi(UI_PATH, self)
        self.resize(1500, 800)

        self.__blocks = None

        self.ui_dag_widget = dagView.DagWidget()
        self.setCentralWidget(self.ui_dag_widget)

        # create dock widgets
        self.ui_size_chart = DockChart(self)
        self.ui_size_chart.setWindowTitle('Size distribution chart')
        self.ui_type_chart = DockChart(self)
        self.ui_type_chart.setWindowTitle('Dag type distribution chart')

        self.ui_info_table = DockTable(info.Info, self)
        self.ui_req_table = DockTable(requirement.Requirement, self)
        self.ui_config_table = DockTable(config.Config, self)
        self.ui_ref_table = DockTable(reference.Reference, self)
        self.ui_audio_table = DockTable(audio.Audio, self)

        self.ui_progress = QtWidgets.QProgressBar()
        self.ui_progress.setVisible(False)
        self.statusBar().addPermanentWidget(self.ui_progress)

        self.ui_open_action.triggered.connect(self.load)
        self.ui_clear_action.triggered.connect(self.clear)
        self.ui_reset_action.triggered.connect(self.reset)

    def clear(self):
        # the order matters
        for widget in [
            self.ui_size_chart,
            self.ui_type_chart,
            self.ui_info_table,
            self.ui_req_table,
            self.ui_config_table,
            self.ui_ref_table,
            self.ui_audio_table,
        ]:
            widget.clear()

        self.ui_dag_widget.clear()

    def reset(self):
        for widget in [
            self.ui_size_chart,
            self.ui_type_chart,
            self.ui_info_table,
            self.ui_req_table,
            self.ui_config_table,
            self.ui_ref_table,
            self.ui_audio_table,
        ]:
            widget.reset()

    def load(self):
        from guiUtil import prompt

        mfile = prompt.get_path_import(default_path=PROJECT_DIR, typ='*.ma')

        if not mfile:
            return

        if not os.path.exists(mfile):
            prompt.message("File not found \n{}".format(mfile), prompt.ERROR)
            return

        self.__get_blocks(mfile)

        self.clear()
        self.update()

    def update(self):
        self.__update_dag_view()
        self.__update_size_chart()
        self.__update_info_table()

    def __get_blocks(self, mfile):
        loader = asciiLoader.LoadThread()
        loader.progress_changed.connect(lambda value: update_progress(self.ui_progress, value))
        loader.event_occurred.connect(lambda msg: update_message(self.statusBar(), msg))
        self.__blocks = loader.load(mfile)

    def __update_dag_view(self):
        buider = dagBuilder.BuildThread()
        buider.progress_changed.connect(lambda value: update_progress(self.ui_progress, value))
        buider.event_occurred.connect(lambda msg: update_message(self.statusBar(), msg))
        root = buider.build(self.__blocks)

        children = dagNode.get_children(root)
        results = dagNode.get_distribution(children, top=10)
        for i in range(len(results)):
            self.ui_type_chart.add_slice(
                results[i][0],
                results[i][1],
                palette.TABLEAU_NEW_10[i]
            )

        self.ui_dag_widget.set_root(root)
        self.ui_dag_widget.update()

    def __update_size_chart(self):
        # simple chart
        results = asciiBlock.get_distribution(self.__blocks)
        for i in range(len(results)):
            self.ui_size_chart.add_slice(
                results[i][0],
                results[i][1],
                palette.PRIM_3[i]
            )

    def __update_info_table(self):
        infos = info.Info.from_blocks(self.__blocks)
        for entry in infos:
            self.ui_info_table.add_entry(entry)

        reqs = requirement.Requirement.from_blocks(self.__blocks)
        for entry in reqs:
            self.ui_req_table.add_entry(entry)

        conf = config.Config.from_blocks(self.__blocks)
        self.ui_config_table.add_entry(conf)

        refs = reference.Reference.from_blocks(self.__blocks)
        for entry in refs:
            self.ui_ref_table.add_entry(entry)

        audios = audio.Audio.blocks(self.__blocks)
        for entry in audios:
            self.ui_audio_table.add_entry(entry)


def update_progress(progress_bar, value):
    progress_bar.setValue(value)

    if value >= 100:
        progress_bar.setVisible(False)
    elif progress_bar.isHidden():
        progress_bar.setVisible(True)


def update_message(status_bar, msg):
    status_bar.showMessage(msg, 2000)


def show():
    from qt_material import apply_stylesheet
    global window

    import ctypes
    app_id = 'xingyulei.asciiviewer.1-0-0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    extra = {
        'font_size': '10px',
        'density_scale': '-1',
    }

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(ICON_PATH))
    apply_stylesheet(app, theme='light_blue.xml', extra=extra)

    window = AsciiViewer()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    show()
