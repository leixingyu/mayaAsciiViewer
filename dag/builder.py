import time

from Qt import QtCore

from . import dagNode
from .. import asciiData


class BuildThread(QtCore.QThread):
    progress_changed = QtCore.Signal(int)
    event_occurred = QtCore.Signal(str)

    def build(self, datas):
        """
        Create node networks from NodeData

        :param datas: list of NodeData(s). ascii data starting with 'createNode'
        :return: NodeData. root node data
        """
        start_time = time.time()
        self.event_occurred.emit('Building DAG Tree')
        root_node = dagNode.DagNode()
        nodes = list()

        for i, data in enumerate(datas):
            if not isinstance(data, asciiData.NodeData):
                raise TypeError

            node = dagNode.DagNode(data.name, data.dtype, data.size, data.index)
            nodes.append(node)
            self.progress_changed.emit(int(float(len(nodes)) / len(datas) * 100))

            parent = None
            if data.parent:
                while i > 0:
                    i -= 1
                    # sometimes the name contains '|'
                    if data.parent.endswith(datas[i].name):
                        parent = nodes[i]
                        break

                if not parent:
                    raise ValueError(
                        'Parent {} not found'.format(data.parent)
                    )
            else:
                parent = root_node

            node.set_parent(parent)

        time_elapsed = round(time.time() - start_time, 3)
        self.event_occurred.emit('Build Complete: {}s'.format(time_elapsed))

        return root_node
