import logging
from collections import OrderedDict

from mayaAsciiParser import asciiData, loader
from mayaAsciiParser.data import audioData, configData

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def search():
    p = r"C:\Users\Lei\Desktop\test.ma"

    load_thread = loader.LoadThread()
    datas = load_thread.load(p)
    datas = sorted(datas, key=lambda n: n.size, reverse=1)
    datas = [asciiData.new(data) for data in datas]

    print audioData.get(datas)
    print configData.get(datas)


def test():
    p = r"C:\Users\Lei\Desktop\maya-example-scene\rig\kayla_v1.9\kayla2017\kayla2017.ma"

    load_thread = loader.LoadThread()
    datas = load_thread.load(p)
    datas = sorted(datas, key=lambda n: n.size, reverse=1)
    datas = [asciiData.new(data) for data in datas]

    # size distribution
    create_size = 0
    connect_size = 0
    for data in datas:
        if isinstance(data, asciiData.NodeData):
            create_size += data.size

        elif isinstance(data, asciiData.ConnectionData):
            connect_size += data.size

    LOG.info('createNode size: %skb', create_size/1024)
    LOG.info('connectAttr size: %skb', connect_size/1024)

    # createNode size distribution
    ntype = dict()
    for data in datas:
        if not isinstance(data, asciiData.NodeData):
            continue

        if data.dtype not in ntype.keys():
            ntype[data.dtype] = [data]
        else:
            ntype[data.dtype].append(data)

    # add size
    nsize = dict()
    for k, v in ntype.items():
        size = 0
        for data in v:
            size += data.size
        nsize[k] = size

    nsize = OrderedDict(sorted(nsize.items(), key=lambda kv: kv[1], reverse=True))

    result = ''
    for k, v in nsize.items()[:10]:
        result += "\t{} --- size: {}kb, percent: {}%\n".format(
                 k,
                 v/1024,
                 round(v/float(create_size) * 100, 3)
                 )
    LOG.info("top 10 most expensive create data:\n%s", result)


if __name__ == '__main__':
    search()
