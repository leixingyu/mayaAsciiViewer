from Qt import QtWidgets, QtCore, QtGui

from . import dagNode


class DagModel(QtCore.QAbstractItemModel):
    sort_role = QtCore.Qt.UserRole
    filter_role = QtCore.Qt.UserRole + 1

    def __init__(self, root, parent=None):
        """
        Initialization

        :param root: DagNode. the invisible scene root node of the model
        """
        super(DagModel, self).__init__(parent)
        self.__root_node = root

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        Override
        """
        if not parent.isValid():
            parent_node = self.__root_node
        else:
            parent_node = parent.internalPointer()

        return parent_node.child_count

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        Override
        """
        return 4

    def flags(self, index):
        """
        Override
        """
        flags = super(DagModel, self).flags(index)
        return QtCore.Qt.ItemIsEditable | flags

    def data(self, index, role):
        """
        Override
        """
        node = self.get_node(index)

        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            if index.column() == 0:
                return node.name
            elif index.column() == 1:
                return node.typ
            elif index.column() == 2:
                if node.total_size > 1024 * 1024:
                    return '{}MB'.format(
                        round(node.total_size/1024.0/1024, 2)
                    )

                return '{}KB'.format(
                    round(node.total_size/1024.0, 2)
                )
            elif index.column() == 3:
                return round(
                    node.total_size / float(self.__root_node.total_size) * 100
                    )

        elif role == DagModel.sort_role:
            if index.column() == 0:
                return node.name
            elif index.column() == 1:
                return node.typ
            elif index.column() == 2:
                return node.total_size
            elif index.column() == 3:
                return node.total_size

        elif role == DagModel.filter_role:
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
                return "Percentage"

        elif role == QtCore.Qt.InitialSortOrderRole:
            return QtCore.Qt.DescendingOrder

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """
        Override
        """
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parent_node = self.get_node(parent)
        current_node = parent_node.child(row)
        if current_node:
            return self.createIndex(row, column, current_node)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        """
        Override
        """
        current_node = self.get_node(index)
        parent_node = current_node.parent

        if parent_node == self.__root_node:
            return QtCore.QModelIndex()

        return self.createIndex(parent_node.row, 0, parent_node)

    def clear(self):
        """
        Custom: clear the model data
        """
        self.beginResetModel()
        self.__root_node = dagNode.DagNode()
        self.endResetModel()
        return True

    def get_node(self, index=QtCore.QModelIndex()):
        """
        Custom: get DagNode from model index

        :param index: QModelIndex. specified index
        """
        if index.isValid():
            current_node = index.internalPointer()
            if current_node:
                return current_node
        return self.__root_node


class DagProxyModel(QtCore.QSortFilterProxyModel):
    """
    For configuring sorting and filtering
    """

    def __init__(self, *args, **kwargs):
        super(DagProxyModel, self).__init__(*args, **kwargs)

        # sorting
        self.setDynamicSortFilter(False)
        self.setSortRole(DagModel.sort_role)
        self.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # filtering
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setFilterRole(DagModel.filter_role)
        self.setFilterKeyColumn(0)
