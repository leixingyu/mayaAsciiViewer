"""
Module for evoking the main GUI
"""

import os
import sys

from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi
from guiUtil.template import pieChart, table

from mayaAsciiViewer import asciiBlock, asciiLoader
from mayaAsciiViewer.block import audio, config, reference, requirement, info
from mayaAsciiViewer.dag import dagBuilder, dagView, dagNode


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(MODULE_PATH, 'asciiViewer.ui')
ICON_PATH = os.path.join(MODULE_PATH, 'icon.png')
PROJECT_DIR = os.path.expandvars("%USERPROFILE%\\Desktop")

# color palette
TABLEAU_NEW_10 = [
    '#4e79a7',
    '#59a14f',
    '#9c755f',
    '#f28e2b',
    '#edc948',
    '#bab0ac',
    '#e15759',
    '#b07aa1',
    '#76b7b2',
    '#ff9da7',
]
PRIM_3 = [
    '#82d3e5',
    '#fd635c',
    '#feb543',
]


class DockChart(QtWidgets.QDockWidget):
    """
    Class for creating dockable pie chart widget
    """
    def __init__(self, parent):
        """
        Initialization
        """
        super(DockChart, self).__init__(parent)
        self.__parent = parent

        self.__chart = pieChart.SimpleChart()
        self.__chart.resize(500, 300)

        chart_view = pieChart.SimpleChartView(self.__chart)
        self.setWidget(chart_view)

        self.dock()

    def dock(self, position=QtCore.Qt.RightDockWidgetArea):
        """
        Dock the current widget to parent

        :param position: Qt.DockWidgetArea. target dock position
        """
        self.__parent.addDockWidget(position, self)

    def clear(self):
        """
        Clear all existing data in the widget
        """
        self.restore()
        self.__chart.clear()

    def restore(self):
        """
        Restore the widget to its default position
        """
        if self.isFloating():
            self.setFloating(False)
        if not self.isVisible():
            self.setVisible(True)
        self.dock()

    def add_slice(self, name, value, color):
        """
        Add a data/slice to the pie chart

        :param name: str. name of the slice
        :param value: int. value of the slice
        :param color: QColor. color of the slice
        """
        self.__chart.add_slice(name, value, color)


class DockTable(QtWidgets.QDockWidget):
    """
    Class for creating dockable table widget
    """
    def __init__(self, cls, parent):
        """
        Initialization

        :param cls: namedtuple. data class to be presented in the table
        """
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
        """
        Dock the current widget to parent

        :param position: Qt.DockWidgetArea. target dock position
        """
        self.__parent.addDockWidget(position, self)

    def clear(self):
        """
        Clear all existing data in the widget
        """
        self.restore()
        self.__table.setRowCount(0)

    def restore(self):
        """
        Restore the widget to its default position
        """
        if self.isFloating():
            self.setFloating(False)
        if not self.isVisible():
            self.setVisible(True)
        self.dock()

    def add_entry(self, values):
        """
        Add an entry to the table

        :param values: list. data entries corresponding to each header
        """
        self.__table.insertRow(self.__table.rowCount())
        for i, arg in enumerate(self.__args):
            self.__table.setItem(
                self.__table.rowCount()-1,
                i,
                QtWidgets.QTableWidgetItem(str(values[i]))
            )


class AsciiViewer(QtWidgets.QMainWindow):
    """
    Create the ascii viewer main application window
    """
    def __init__(self):
        """
        Initialization
        """
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

        # store the order
        self.ui_dockables = [
            self.ui_size_chart,
            self.ui_type_chart,
            self.ui_info_table,
            self.ui_req_table,
            self.ui_config_table,
            self.ui_ref_table,
            self.ui_audio_table,
        ]

        self.ui_progress = QtWidgets.QProgressBar()
        self.ui_progress.setVisible(False)
        self.statusBar().addPermanentWidget(self.ui_progress)

        # connect signals
        self.ui_open_action.triggered.connect(self.load)
        self.ui_clear_action.triggered.connect(self.clear)
        self.ui_reset_action.triggered.connect(self.restore)

    def clear(self):
        """
        Clear all existing data in all widgets
        """
        # order matters for docking position
        for widget in self.ui_dockables:
            widget.clear()

        self.ui_dag_widget.clear()

    def restore(self):
        """
        Restore all widgets to its default position
        """
        # order matters for docking position
        for widget in self.ui_dockables:
            widget.restore()

    def load(self):
        """
        Load a maya ascii file for viewing, populates all widgets with file
        data.
        """
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
        """
        Update all widgets to reflect the latest ascii blocks data
        """
        self.__update_dag_view()
        self.__update_size_chart()
        self.__update_tables()

    def __get_blocks(self, mfile):
        """
        Update the latest ascii blocks data

        :param mfile: str. file path to a maya ascii file
        """
        loader = asciiLoader.Loader()
        loader.progress_changed.connect(lambda value: update_progress(self.ui_progress, value))
        loader.event_occurred.connect(lambda msg: update_message(self.statusBar(), msg))
        self.__blocks = loader.load(mfile)

    def __update_dag_view(self):
        """
        Update the Dag view and the Dag type chart
        to reflect the latest ascii blocks data
        """
        buider = dagBuilder.Builder()
        buider.progress_changed.connect(lambda value: update_progress(self.ui_progress, value))
        buider.event_occurred.connect(lambda msg: update_message(self.statusBar(), msg))
        root = buider.build(self.__blocks)

        children = dagNode.get_children(root)
        results = dagNode.get_distribution(children, top=10)
        for i in range(len(results)):
            self.ui_type_chart.add_slice(
                results[i][0],
                results[i][1],
                TABLEAU_NEW_10[i]
            )

        self.ui_dag_widget.set_root(root)
        self.ui_dag_widget.update()

    def __update_size_chart(self):
        """
        Update the size chart to reflect the latest ascii blocks data
        """
        # simple chart
        results = asciiBlock.get_distribution(self.__blocks)
        for i in range(len(results)):
            self.ui_size_chart.add_slice(
                results[i][0],
                results[i][1],
                PRIM_3[i]
            )

    def __update_tables(self):
        """
        Update the tables to reflect the latest ascii blocks data
        """
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

        audios = audio.Audio.from_blocks(self.__blocks)
        for entry in audios:
            self.ui_audio_table.add_entry(entry)


def update_progress(progress_bar, value):
    """
    Update a progress bar widget with given value

    :param progress_bar: QtWidget.QProgressBar. progress to update
    :param value: int. progress value
    """
    progress_bar.setValue(value)

    if value >= 100:
        progress_bar.setVisible(False)
    elif progress_bar.isHidden():
        progress_bar.setVisible(True)
    QtCore.QCoreApplication.processEvents()


def update_message(status_bar, msg):
    """
    Display a given string in status bar widget

    :param status_bar: QtWidget.QStatusBar. status bar to update
    :param msg: str. message to display
    """
    status_bar.showMessage(msg, 2000)
    QtCore.QCoreApplication.processEvents()


def show():
    """
    Launch the main application with custom icon and style sheet
    """
    import ctypes

    global window

    app_id = 'xingyulei.asciiviewer.1-0-0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(ICON_PATH))

    try:
        from qt_material import apply_stylesheet
        extra = {
            'density_scale': '-1',
        }
        apply_stylesheet(app, theme='light_blue.xml', extra=extra)
    except ImportError:
        pass

    window = AsciiViewer()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    show()
