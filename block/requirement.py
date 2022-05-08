"""
Example:

requires -nodeType "HIKSkeletonGeneratorNode" -dataType "HIKCharacter" -dataType "HIKCharacterState"
        -dataType "HIKEffectorState" -dataType "HIKPropertySetState" "mayaHIK" "1.0_HIK_2016.5";

requires "mtoa" "3.2.0.2";
"""

from collections import namedtuple

from .. import asciiBlock


RequirementBase = namedtuple('RequirementBase',
                             ['product', 'version', 'data_type', 'node_type'])


class Requirement(RequirementBase):
    @classmethod
    def from_blocks(cls, blocks):
        references = list()
        for block in blocks:
            if not isinstance(block, asciiBlock.RequirementBlock):
                continue
    
            references.append(
                RequirementBase(
                    block.product,
                    block.version,
                    block.data_type,
                    block.node_type)
            )
    
        return references
