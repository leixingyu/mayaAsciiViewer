"""

f = 'D:\\testbin\\maya-file.ma'
ma = MayaAscii(f)

with open("C:\Users\\Lei\\Downloads\\output.txt", "w") as file:
    file.write(ma.diagnose_usage())

"""

from . import asciiNode


def diagnose_usage(path):
    output = ''

    # sort
    nodes = asciiNode.AsciiNode.from_file(path)
    nodes = sorted(nodes, key=lambda n: n.size, reverse=1)

    for node in nodes:
        # filter
        if node.percent < 0.1:
            continue

        line = "[line: {index}][{size} mb][{percent}%] {description} \n".format(
            index=node.index,
            description=node.description,
            percent=node.percent,
            size=round(node.size / float(1024) / float(1024), 3)
        )
        output += line

    return output


def parse_node_by_type(path, ntype):
    """

    common node type: 'createNode' 'connectAttr'
    :param path:
    :param ntype:
    :return:
    """

    nodes = asciiNode.AsciiNode.from_file(path)
    return [node for node in nodes if node.desc.startswith(ntype)]


def tokenize_command(line):
    """

    Source: https://github.com/mottosso/maya-scenefile-parser/

    :param line: str
    :return:
    """
    command, _, line = line.partition(" ")
    command = command.lstrip()

    args = list()
    while True:
        line = line.strip()

        if not line:
            break

        # handle quotation marks in string
        if line[0] in ['\"', "\'"]:
            string_delim = line[0]
            escaped = False
            string_end = len(line)

            # find the closing quote as string end
            for i in range(1, len(line)):
                if not escaped and line[i] == string_delim:
                    string_end = i
                    break
                elif not escaped and line[i] == "\\":
                    escaped = True
                else:
                    escaped = False

            arg, line = line[1:string_end], line[string_end+1:]

        else:
            arg, _, line = line.partition(" ")

        args.append(arg)

    return command, args

