import logging
from collections import OrderedDict

from mayaAsciiParser import ascii, asciiNode, nodeFactory, createNode, connectNode

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


if __name__ == "__main__":

    p = r"C:\Users\Lei\Desktop\test.ma"

    # initialize nodes
    nodes = asciiNode.AsciiNode.from_file(p)
    asc = ascii.Ascii(p)
    nodes = sorted(nodes, key=lambda n: n.size, reverse=1)
    nodes = [nodeFactory.NodeFactory(node) for node in nodes]

    # size distribution
    create_size = 0
    connect_size = 0
    for node in nodes:
        if isinstance(node, createNode.CreateNode):
            create_size += node.size

        elif isinstance(node, connectNode.ConnectNode):
            connect_size += node.size

    LOG.info('createNode size: %skb; percent: %s%%',
             create_size/1024,
             round(create_size/float(asc.size)*100, 2)
             )
    LOG.info('connectAttr size: %skb; percent: %s%%',
             connect_size/1024,
             round(connect_size/float(asc.size)*100, 2)
             )

    # createNode size distribution

    # group by type
    ntype = dict()
    for node in nodes:
        if not isinstance(node, createNode.CreateNode):
            continue

        if node.type not in ntype.keys():
            ntype[node.type] = [node]
        else:
            ntype[node.type].append(node)

    # add size
    nsize = dict()
    for k, v in ntype.items():
        size = 0
        for node in v:
            size += node.size
        nsize[k] = size

    nsize = OrderedDict(sorted(nsize.items(), key=lambda kv: kv[1], reverse=True))

    result = ''
    for k, v in nsize.items()[:10]:
        result += "\t{} --- size: {}kb, percent: {}%\n".format(
                 k,
                 v/1024,
                 round(v/float(create_size) * 100, 3)
                 )
    LOG.info("top 10 most expensive create node:\n%s", result)
