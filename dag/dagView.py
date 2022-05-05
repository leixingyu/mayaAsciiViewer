from Qt import QtWidgets, QtCore, QtGui

from . import dagModel


class PercentageDelegate(QtWidgets.QItemDelegate):

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QProgressBar(parent)
        editor.setMinimum(0)
        editor.setMaximum(100)
        return editor

    def setEditorData(self, editor, index):
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
        editor.setStyleSheet(style)


class DagView(QtWidgets.QTreeView):
    PERCENT_COLUMN = 3

    def __init__(self, parent=None):
        super(DagView, self).__init__(parent)

        self.__model = None
        self.__proxy_model = dagModel.DagProxyModel(self)
        self.__delegate = PercentageDelegate(self)

        self.setModel(self.__proxy_model)
        self.setItemDelegateForColumn(self.PERCENT_COLUMN, self.__delegate)

        self.expanded.connect(self.__make_children_persistent)

    def set_root(self, node):
        self.__model = dagModel.DagModel(node, self)
        self.__proxy_model.setSourceModel(self.__model)

    def clear(self):
        # FIXME: this doesn't work correctly
        if self.model().sourceModel():
            self.model().sourceModel().clear()

    def update(self):
        self.sortByColumn(self.PERCENT_COLUMN, QtCore.Qt.DescendingOrder)
        self.__make_children_persistent()

    def __make_children_persistent(self, index=QtCore.QModelIndex()):
        for row in range(0, self.__proxy_model.rowCount(index)):
            # top level
            if index == QtCore.QModelIndex():
                child = self.__proxy_model.index(row, self.PERCENT_COLUMN)
            # non-top level
            else:
                child = index.child(row, self.PERCENT_COLUMN)

            self.openPersistentEditor(child)
