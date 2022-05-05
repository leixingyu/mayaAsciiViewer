import os
import sys

from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi
from guiUtil.template import pieChart
from pipelineUtil.data import palette

from mayaAsciiParser import asciiBlock, asciiLoader
from mayaAsciiParser.block import audio, config, reference, requirement, info
from mayaAsciiParser.dag import dagModel, dagBuilder, dagView, dagNode


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(MODULE_PATH, 'asciiViewer.ui')
PROJECT_DIR = r"C:\Users\Lei\Desktop\maya-example-scene"


class DockChart(QtWidgets.QDockWidget):

    def __init__(self, parent=None):
        super(DockChart, self).__init__(parent)

        self.__chart = pieChart.SimpleChart()
        self.__chart.resize(500, 300)

        chart_view = pieChart.SimpleChartView(self.__chart)
        self.setWidget(chart_view)

    def add_slice(self, name, value, color):
        self.__chart.add_slice(name, value, color)


class DockTable(QtWidgets.QDockWidget):
    def __init__(self, cls, parent=None):
        super(DockTable, self).__init__(parent)
        self.setWindowTitle(cls.__name__)

        self.__args = cls._fields
        self.__table = QtWidgets.QTableWidget()
        self.__table.setColumnCount(len(self.__args))
        self.__table.setHorizontalHeaderLabels(self.__args)

        for i in range(self.__table.columnCount()):
            self.__table.horizontalHeader().setSectionResizeMode(
                i,
                QtWidgets.QHeaderView.Interactive
            )

        self.setWidget(self.__table)

    def add_entry(self, values):
        self.__table.insertRow(self.__table.rowCount())
        for i, arg in enumerate(self.__args):
            self.__table.setItem(
                self.__table.rowCount()-1,
                i,
                QtWidgets.QTableWidgetItem(str(values[i]))
            )


class AsciiViewer(QtWidgets.QMainWindow):

    def __init__(self):
        super(AsciiViewer, self).__init__()
        _loadUi(UI_PATH, self)

        self.__blocks = None

        self.ui_tree_view = dagView.DagView()
        self.ui_grid_layout.addWidget(self.ui_tree_view, 0, 0)

        # create dock widgets
        self.ui_size_chart = DockChart()
        self.ui_type_chart = DockChart()
        self.ui_info_table = DockTable(info.Info)
        self.ui_req_table = DockTable(requirement.Requirement)
        self.ui_config_table = DockTable(config.Config)
        self.ui_ref_table = DockTable(reference.Reference)
        self.ui_audio_table = DockTable(audio.Audio)

        for chart in [self.ui_size_chart, self.ui_type_chart]:
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, chart)

        for table in [self.ui_info_table, self.ui_ref_table, self.ui_config_table, self.ui_req_table, self.ui_audio_table]:
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, table)

        self.ui_progress = QtWidgets.QProgressBar()
        self.ui_progress.setVisible(False)
        self.statusBar().addPermanentWidget(self.ui_progress)

        self.ui_open_action.triggered.connect(self.load)

    def load(self):
        from guiUtil import prompt

        mfile = prompt.get_path_import(default_path=PROJECT_DIR, typ='*.ma')

        if not mfile:
            prompt.message("Cancelled by User", prompt.ERROR)
            return

        if not os.path.exists(mfile):
            prompt.message("File not found \n{}".format(mfile), prompt.ERROR)
            return

        self.__get_blocks(mfile)

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

        self.ui_tree_view.set_root(root)
        self.ui_tree_view.update()

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

    extra = {
        'font_size': '10px',
        'density_scale': '-1',
    }

    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml', extra=extra)

    window = AsciiViewer()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    show()
