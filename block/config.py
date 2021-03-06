"""
Module used to parse scene configuration from ascii data blocks

Scripting:
```
# maya file min and max animation playback slider
config = Config.from_blocks(blocks)
print(config.min, config.max)
```

Example:
```
createNode script -n "sceneConfigurationScriptNode";
    rename -uid "ABFFC671-4DDD-54FB-0647-B594FEE16B08";
    setAttr ".b" -type "string" "playbackOptions -min 258 -max 317 -ast 1 -aet 2160 ";
    setAttr ".st" 6;
```

"""

import re
from collections import namedtuple

from .. import asciiBlock


ConfigBase = namedtuple('ConfigBase', ['min', 'max', 'start', 'end'])


class Config(ConfigBase):
    @classmethod
    def from_blocks(cls, blocks):
        """
        Create scene configuration data object from ascii data blocks

        :param blocks: list of AsciiBlock.
                       normally generated from 'asciiLoader.py'
        :return: Config. scene configuration object
        """
        for block in blocks:
            if not isinstance(block, asciiBlock.NodeBlock):
                continue
    
            if block.name != 'sceneConfigurationScriptNode':
                continue
    
            detail = block.asc.read_detail(block.index)
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
