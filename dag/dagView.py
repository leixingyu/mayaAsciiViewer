"""
A view module that supports Dag node for Model View Programming in Qt
"""


from Qt import QtWidgets, QtCore, QtGui

from . import dagModel


class DagView(QtWidgets.QTreeView):
    """
    Main Dag tree view
    """
    PERCENT_COLUMN = 3

    def __init__(self, parent=None):
        super(DagView, self).__init__(parent)

        self.setSortingEnabled(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.__model = dagModel.DagModel('')
        self.proxy_model = dagModel.DagProxyModel(self)
        self.__delegate = PercentageDelegate(self)

        self.setModel(self.proxy_model)
        self.setItemDelegateForColumn(self.PERCENT_COLUMN, self.__delegate)

        self.expanded.connect(self.__make_children_persistent)

    def set_root(self, node):
        self.__model = dagModel.DagModel(node, self)
        self.proxy_model.setSourceModel(self.__model)
        # after remove filtering
        self.proxy_model.rowsInserted.connect(self.__make_children_persistent)

    def clear(self):
        if self.model().sourceModel():
            self.model().sourceModel().clear()

    def update(self):
        self.sortByColumn(self.PERCENT_COLUMN, QtCore.Qt.DescendingOrder)
        self.__make_children_persistent()

    def __make_children_persistent(self, index=QtCore.QModelIndex()):
        # TODO: only make persistent on items visible on screen
        for row in range(0, self.proxy_model.rowCount(index)):
            # top level
            if index == QtCore.QModelIndex():
                child = self.proxy_model.index(row, self.PERCENT_COLUMN)
            # non-top level
            else:
                child = index.child(row, self.PERCENT_COLUMN)

            self.openPersistentEditor(child)


class DagWidget(QtWidgets.QWidget):
    """
    A widget wrapper for main Dag view that also includes a line edit for
    filtering
    """
    def __init__(self):
        super(DagWidget, self).__init__()

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self.ui_filter_edit = QtWidgets.QLineEdit()
        self.ui_dag_view = DagView()

        layout.addWidget(self.ui_filter_edit, 0, 0)
        layout.addWidget(self.ui_dag_view, 1, 0)

        self.ui_filter_edit.textChanged.connect(
            self.ui_dag_view.proxy_model.setFilterRegExp)

    def set_root(self, node):
        self.ui_dag_view.set_root(node)

    def update(self):
        self.ui_dag_view.update()

    def clear(self):
        self.ui_filter_edit.setText('')
        self.ui_dag_view.clear()


class PercentageDelegate(QtWidgets.QItemDelegate):
    """
    For creating a qt graphic delegate used in the main dag view
    """
    def createEditor(self, parent, option, index):
        """
        Override
        """
        editor = QtWidgets.QProgressBar(parent)
        editor.setMinimum(0.0)
        editor.setMaximum(100.0)
        return editor

    def setEditorData(self, editor, index):
        """
        Override
        """
        model_value = index.model().data(index, QtCore.Qt.EditRole)
        color = [
            '#c0ff33',
            '#feff5c',
            '#ffc163',
            '#ffa879',
            '#fb4b4b',
            '#fb4b4b'
        ][int(model_value / 20)]

        style = (
            """
            QProgressBar {{
                border: 1px solid grey;
                text-align: center;
                color: '';
            }}

            QProgressBar::chunk {{
                background-color: {};
            }}
            """.format(color)
        )

        editor.setValue(model_value)
        editor.setFormat('{}%'.format(model_value))
        if model_value < 0.1:
            editor.setFormat('<0.1%')
        editor.setStyleSheet(style)
