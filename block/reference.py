"""
Example:

file -r -ns "tracer" -dr 1 -rfn "tracerRN" -op "v=0;" -typ "mayaAscii" "C:/Users/tracer.ma";
"""

from collections import namedtuple

from .. import asciiBlock


ReferenceBase = namedtuple('ReferenceBase',
                           ['path', 'ref_node', 'namespace', 'typ'])


class Reference(ReferenceBase):
    @classmethod
    def from_blocks(cls, blocks):
        references = list()
        for block in blocks:
            if not isinstance(block, asciiBlock.FileBlock):
                continue
    
            if not block.is_ref:
                continue
    
            references.append(ReferenceBase(
                block.path,
                block.ref_node,
                block.namespace,
                block.typ)
            )
        return references
