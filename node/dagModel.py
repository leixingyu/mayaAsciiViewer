from Qt import QtWidgets, QtCore, QtGui

from . import dagNode


class DagModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1

    def __init__(self, root, parent=None):
        """
        Initialization
        :param root: QJsonNode. root node of the model, it is hidden
        """
        super(DagModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        Override
        """
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.child_count

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        Override
        """
        return 5

    def data(self, index, role):
        """
        Override
        """
        node = self.getNode(index)

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return node.name
            elif index.column() == 1:
                return node.ntype
            elif index.column() == 2:
                return node.total_size
            elif index.column() == 3:
                return node.size

        elif role == DagModel.sortRole:
            if index.column() == 0:
                return node.name
            elif index.column() == 1:
                return node.ntype
            elif index.column() == 2:
                return node.total_size
            elif index.column() == 3:
                return node.size

        elif role == DagModel.filterRole:
            return node.name

        elif role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(-1, 22)

    def headerData(self, section, orientation, role):
        """
        Override
        """
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Type"
            elif section == 2:
                return "Size"
            else:
                return "More"

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """
        Override
        """
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parentNode = self.getNode(parent)
        currentNode = parentNode.child(row)
        if currentNode:
            return self.createIndex(row, column, currentNode)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        """
        Override
        """
        currentNode = self.getNode(index)
        parentNode = currentNode.parent

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def addChildren(self, children, parent=QtCore.QModelIndex()):
        """
        Custom: add children QJsonNode to the specified index
        """
        self.beginInsertRows(parent, 0, len(children) - 1)

        if parent == QtCore.QModelIndex():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        for child in children:
            parentNode.addChild(child)

        self.endInsertRows()
        return True

    def removeChild(self, position, parent=QtCore.QModelIndex()):
        """
        Custom: remove child of position for the specified index
        """
        self.beginRemoveRows(parent, position, position)

        if parent == QtCore.QModelIndex():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        parentNode.removeChild(position)

        self.endRemoveRows()
        return True

    def clear(self):
        """
        Custom: clear the model data
        """
        self.beginResetModel()
        self._rootNode = dagNode.DagNode()
        self.endResetModel()
        return True

    def getNode(self, index):
        """
        Custom: get QJsonNode from model index
        :param index: QModelIndex. specified index
        """
        if index.isValid():
            currentNode = index.internalPointer()
            if currentNode:
                return currentNode
        return self._rootNode
