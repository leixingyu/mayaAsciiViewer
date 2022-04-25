"""
Example:


createNode script -n "sceneConfigurationScriptNode";
    rename -uid "ABFFC671-4DDD-54FB-0647-B594FEE16B08";
    setAttr ".b" -type "string" "playbackOptions -min 258 -max 317 -ast 1 -aet 2160 ";
    setAttr ".st" 6;
"""

import re
from collections import namedtuple

from .. import asciiData


ConfigBase = namedtuple('ConfigBase', ['min', 'max', 'start', 'end'])


class Config(ConfigBase):
    @classmethod
    def from_datas(cls, datas):
        for data in datas:
            if not isinstance(data, asciiData.NodeData):
                continue
    
            if data.name != 'sceneConfigurationScriptNode':
                continue
    
            detail = data.asc.read_detail(data.index)
            # default
            script_re = re.compile('.*setAttr ".b" -type "string" "(.*)";')
            script = script_re.search(detail).group(1)
    
            # playback option
            playback_re = re.compile(r'.*playbackOptions '
                                     r'-min (?P<min>[-+]?[0-9]*\.?[0-9]*) '
                                     r'-max (?P<max>[-+]?[0-9]*\.?[0-9]*) '
                                     r'-ast (?P<ast>[-+]?[0-9]*\.?[0-9]*) '
                                     r'-aet (?P<aet>[-+]?[0-9]*\.?[0-9]*)')
            match = playback_re.search(script)
            if match:
                min = match.group('min')
                max = match.group('max')
                ast = match.group('ast')
                aet = match.group('aet')
                return cls(float(min), float(max), float(ast), float(aet))
