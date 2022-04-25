"""
Example:

file -r -ns "tracer" -dr 1 -rfn "tracerRN" -op "v=0;" -typ "mayaAscii" "C:/Users/tracer.ma";
"""

from collections import namedtuple

from .. import asciiData


ReferenceBase = namedtuple('ReferenceBase', ['path', 'rfn', 'ns', 'typ'])


class Reference(ReferenceBase):
    @classmethod
    def from_datas(cls, datas):
        references = list()
        for data in datas:
            if not isinstance(data, asciiData.FileData):
                continue
    
            if not data.r:
                continue
    
            references.append(ReferenceBase(data.path, data.rfn, data.ns, data.typ))
    
        return references
