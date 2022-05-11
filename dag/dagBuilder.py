"""
Module to maya dag node tree building

Example
```python
builder = Builder()

# the invisible root of all top level dag nodes
root = builder.build(blocks)
```

`progress_changed` signal can be connected to progress bar to reflect load
progress and `event_occurred` can be connected to status bar to display
event message
"""


import time

from Qt import QtCore

from . import dagNode
from .. import asciiBlock


class Builder(QtCore.QObject):
    """
    Builder for creating Dag node tree
    this should be the standard way of creating a tree of Dag nodes consists
    with an ascii file, which we will need to use the asciiLoader.py to
    generate ascii data blocks.
    """
    progress_changed = QtCore.Signal(int)
    event_occurred = QtCore.Signal(str)

    def build(self, blocks):
        """
        Create node networks from Ascii data blocks

        :param blocks: list of AsciiBlock(s). ascii block starting with 'createNode'
        :return: DagNode. root dag node
        """
        # filter data blocks to NodeBlock type
        blocks = [b for b in blocks if isinstance(b, asciiBlock.NodeBlock)]

        start_time = time.time()
        self.event_occurred.emit('Building DAG Tree')
        root_node = dagNode.DagNode()
        nodes = list()

        for i, block in enumerate(blocks):
            if not isinstance(block, asciiBlock.NodeBlock):
                raise TypeError

            node = dagNode.DagNode(block.name, block.typ, block.size, block.index)
            nodes.append(node)
            self.progress_changed.emit(int(float(len(nodes)) / len(blocks) * 100))

            parent = None
            if block.parent:
                while i > 0:
                    i -= 1
                    # sometimes the name contains '|'
                    if block.parent.endswith(blocks[i].name):
                        parent = nodes[i]
                        break

                if not parent:

                    raise ValueError('Parent {} not found'.format(block.parent))
            else:
                parent = root_node

            node.set_parent(parent)

        time_elapsed = round(time.time() - start_time, 3)
        self.event_occurred.emit('Build Complete: {}s'.format(time_elapsed))

        return root_node
