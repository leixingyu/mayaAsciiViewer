"""
Example:

requires -nodeType "HIKSkeletonGeneratorNode" -dataType "HIKCharacter" -dataType "HIKCharacterState"
        -dataType "HIKEffectorState" -dataType "HIKPropertySetState" "mayaHIK" "1.0_HIK_2016.5";

requires "mtoa" "3.2.0.2";
"""

from collections import namedtuple

from .. import asciiData


RequirementBase = namedtuple('RequirementBase', ['product', 'version', 'data_type', 'node_type'])


class Requirement(RequirementBase):
    @classmethod
    def from_datas(cls, datas):
        references = list()
        for data in datas:
            if not isinstance(data, asciiData.RequirementData):
                continue
    
            references.append(
                RequirementBase(data.product, data.version, data.data_type, data.data_type)
            )
    
        return references
