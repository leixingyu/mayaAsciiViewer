"""
Example:

createNode audio -n "happy_frog";
    rename -uid "4D97ED00-45A7-3DF0-4531-63ACF0545B24";
    setAttr ".ef" 2188.9502562925172;
    setAttr ".se" 2188.9502562925172;
    setAttr ".f" -type "string" "C:/Users/Lei/bgm/happy-frog.wav";
"""

import re
from collections import namedtuple

from .. import asciiData


AudioBase = namedtuple('AudioBase', ['name', 'path', 'end_frame', 'source_end', 'source_start', 'offset', 'silence'])


def get(nodes):
    audios = list()

    for node in nodes:
        if not isinstance(node, asciiData.NodeData):
            continue

        if node.dtype != 'audio':
            continue

        detail = node.asc.read_detail(node.index)
        # default
        end_re = re.compile(r'.*setAttr ".se" ([-+]?[0-9]*\.?[0-9]*);')  # source end
        endf_re = re.compile(r'.*setAttr ".ef" ([-+]?[0-9]*\.?[0-9]*);')  # end frame
        path_re = re.compile(r'.*setAttr ".f" -type "string" "(.*)";')
        # optional
        offset_re = re.compile(r'.*setAttr ".o" ([-+]?[0-9]*\.?[0-9]*);')
        start_re = re.compile(r'.*setAttr ".ss" ([-+]?[0-9]*\.?[0-9]*);')  # source start
        silence_re = re.compile(r'.*setAttr ".si" ([-+]?[0-9]*\.?[0-9]*);')

        path = path_re.search(detail).group(1)
        end = float(end_re.search(detail).group(1))
        endf = float(endf_re.search(detail).group(1))

        offset = offset_re.search(detail).group(1) if offset_re.search(detail) else 0
        start = start_re.search(detail).group(1) if start_re.search(detail) else 0
        silence = silence_re.search(detail).group(1) if silence_re.search(detail) else 0

        audios.append(AudioBase(node.name, path, endf, end, start, offset, silence))

    return audios
