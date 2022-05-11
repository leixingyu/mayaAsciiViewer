"""
Module used to parse product and plugin required from ascii data blocks

Scripting:
```
# all product/plugin required name
reqs = Requirement.from_blocks(blocks)
for req in reqs:
    print(req.name)
```

Example:
```
requires -nodeType "HIKSkeletonGeneratorNode" -dataType "HIKCharacter" -dataType "HIKCharacterState"
        -dataType "HIKEffectorState" -dataType "HIKPropertySetState" "mayaHIK" "1.0_HIK_2016.5";
requires "mtoa" "3.2.0.2";
```

"""

from collections import namedtuple

from .. import asciiBlock


RequirementBase = namedtuple('RequirementBase',
                             ['name', 'version', 'data_type', 'node_type'])


class Requirement(RequirementBase):
    @classmethod
    def from_blocks(cls, blocks):
        """
        Create requirements data objects from ascii data blocks

        :param blocks: list of AsciiBlock.
                       normally generated from 'asciiLoader.py'
        :return: list of Requirements. product/plugin requirements objects
        """
        references = list()
        for block in blocks:
            if not isinstance(block, asciiBlock.RequirementBlock):
                continue
    
            references.append(
                RequirementBase(
                    block.name,
                    block.version,
                    block.data_type,
                    block.node_type)
            )
    
        return references
