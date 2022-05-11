"""
Module used to parse references information from ascii data blocks

Scripting:
```
# all references paths
refs = Reference.from_blocks(blocks)
for ref in refs:
    print(ref.path)
```

Example:
```
file -r -ns "test" -dr 1 -rfn "testRN" -op "v=0;" -typ "mayaAscii" "C:/test.ma";
```

"""

from collections import namedtuple

from .. import asciiBlock


ReferenceBase = namedtuple('ReferenceBase',
                           ['path', 'ref_node', 'namespace', 'typ'])


class Reference(ReferenceBase):
    @classmethod
    def from_blocks(cls, blocks):
        """
        Create references data objects from ascii data blocks

        :param blocks: list of AsciiBlock.
                       normally generated from 'asciiLoader.py'
        :return: list of References. references data objects
        """
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
