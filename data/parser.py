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
    def __init__(self, datas, parent=None):
        super(Main, self).__init__(parent)
        self.setFixedSize(QtCore.QSize(600, 400))

        chart = pieChart.MySimpleChart(datas)
        chart_view = pieChart.MyChartView(chart)

        self.setCentralWidget(chart_view)


if __name__ == '__main__':
    global win
    app = QtWidgets.QApplication(sys.argv)

    results = parse(r"C:\Users\Lei\Desktop\test.ma")
    primary_colors = [QtGui.QColor(c) for c in palette.PRIM_3]

    datas = list()
    for i, item in enumerate(['node', 'connection', 'other']):
        data = pieChart.Data(item, results[i], primary_colors[i], '')
        datas.append(data)

    win = Main(datas)
    win.show()
    sys.exit(app.exec_())
