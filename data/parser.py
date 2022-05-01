import logging
import sys

from Qt import QtCore, QtWidgets, QtGui
from guiUtil.template import pieChart
from pipelineUtil.data import palette

from mayaAsciiParser import asciiData, loader
from mayaAsciiParser.data import audio, config, reference, requirement, info

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def search(path):
    datas = loader.LoadThread().load(path)

    conf = config.Config.from_datas(datas)
    print(conf._asdict())

    audios = audio.Audio.from_datas(datas)
    for au in audios:
        print(au._asdict())

    refs = reference.Reference.from_datas(datas)
    for ref in refs:
        print(ref._asdict())

    reqs = requirement.Requirement.from_datas(datas)
    for req in reqs:
        print(req._asdict())

    infos = info.Info.from_datas(datas)
    for i in infos:
        print(i._asdict())


def parse(path):
    node = connection = other = 0
    for data in loader.LoadThread().load(path):
        if isinstance(data, asciiData.NodeData):
            node += data.size
        elif isinstance(data, asciiData.ConnectionData):
            connection += data.size
        else:
            other += data.size
    return [node, connection, other]


class Main(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()

        self.setCentralWidget(widget)
        widget.setLayout(layout)

        ## chart

        results = parse(r"C:\Users\Lei\Desktop\test.ma")
        colors = [c for c in palette.PRIM_3]

        datas = list()
        for i, item in enumerate(['node', 'connection', 'other']):
            data = pieChart.Data(item, results[i], colors[i])
            datas.append(data)

        chart = pieChart.SimpleChart(datas)
        chart.resize(500, 300)
        chart_view = pieChart.SimpleChartView(chart)
        layout.addWidget(chart_view, 0, 0)

        ## tables

        path = r"C:\Users\Lei\Desktop\test.ma"
        data = loader.LoadThread().load(path)

        infos = info.Info.from_datas(data)
        info_table = AbstractTable(info.Info)
        info_table.set_datas(infos)
        layout.addWidget(info_table, 1, 0)

        reqs = requirement.Requirement.from_datas(data)
        req_table = AbstractTable(requirement.Requirement)
        req_table.set_datas(reqs)
        layout.addWidget(req_table, 2, 0)
        
        conf = config.Config.from_datas(data)
        conf_table = AbstractTable(config.Config)
        conf_table.set_datas([conf])
        layout.addWidget(conf_table, 3, 0)


class AbstractTable(QtWidgets.QTableWidget):
    def __init__(self, cls, parent=None):
        """

        :param cls: data class type
        """
        super(AbstractTable, self).__init__(parent)

        self.args = cls._fields

        self.setColumnCount(len(self.args))
        self.setHorizontalHeaderLabels(self.args)
        self.horizontalHeader().setStretchLastSection(1)

    def set_datas(self, datas):
        for data in datas:
            self.insertRow(self.rowCount())
            for i, arg in enumerate(self.args):
                self.setItem(self.rowCount()-1, i, QtWidgets.QTableWidgetItem(str(data[i])))


if __name__ == '__main__':
    global win
    app = QtWidgets.QApplication(sys.argv)

    win = Main()
    win.show()
    sys.exit(app.exec_())
