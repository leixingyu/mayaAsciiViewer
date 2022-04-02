from Qt import QtWidgets, QtCore, QtGui


class View(QtWidgets.QTreeView):

    def __init__(self):
        """
        Initialization
        """
        super(View, self).__init__()

        # set flags
        self.setSortingEnabled(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setUniformRowHeights(True)


    def clear(self):
        """
        Custom: clear the entire view
        """
        self.model().sourceModel().clear()
