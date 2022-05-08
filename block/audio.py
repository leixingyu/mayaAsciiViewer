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

from .. import asciiBlock


AudioBase = namedtuple('AudioBase',
                       ['name',
                        'path',
                        'source_start',
                        'source_end',
                        'end_frame',
                        'offset',
                        'silence']
                       )


class Audio(AudioBase):
    @classmethod
    def blocks(cls, blocks):
        audios = list()

        for block in blocks:
            if not isinstance(block, asciiBlock.NodeBlock):
                continue

            if block.typ != 'audio':
                continue

            detail = block.asc.read_detail(block.index)
            # default
            end_re = re.compile(
                r'.*setAttr ".se" ([-+]?[0-9]*\.?[0-9]*);')  # source end
            endf_re = re.compile(
                r'.*setAttr ".ef" ([-+]?[0-9]*\.?[0-9]*);')  # end frame
            path_re = re.compile(r'.*setAttr ".f" -type "string" "(.*)";')
            # optional
            offset_re = re.compile(r'.*setAttr ".o" ([-+]?[0-9]*\.?[0-9]*);')
            start_re = re.compile(
                r'.*setAttr ".ss" ([-+]?[0-9]*\.?[0-9]*);')  # source start
            silence_re = re.compile(r'.*setAttr ".si" ([-+]?[0-9]*\.?[0-9]*);')

            path = path_re.search(detail).group(1)
            end = float(end_re.search(detail).group(1))
            endf = float(endf_re.search(detail).group(1))

            offset = offset_re.search(detail).group(1) if offset_re.search(
                detail) else 0
            start = start_re.search(detail).group(1) if start_re.search(
                detail) else 0
            silence = silence_re.search(detail).group(1) if silence_re.search(
                detail) else 0

            audios.append(
                cls(block.name, path, start, end, endf, offset, silence)
            )

        return audios
