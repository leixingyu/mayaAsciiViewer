"""
Example:

fileInfo "application" "maya";
fileInfo "product" "Maya 2018";
fileInfo "version" "2018";
fileInfo "cutIdentifier" "201706261615-f9658c4cfc";
fileInfo "osv" "Microsoft Windows 8 Home Premium Edition, 64-bit  (Build 9200)\n";
fileInfo "UUID" "B12C7794-4BD5-04D6-B2AB-D8A7DA8ABDA6";
fileInfo "license" "student";
"""

from collections import namedtuple

from .. import asciiData

InfoBase = namedtuple('InfoBase', ['keyword', 'value'])


class Info(InfoBase):
    @classmethod
    def from_datas(cls, datas):
        infos = list()
        for data in datas:
            if not isinstance(data, asciiData.InfoData):
                continue
            infos.append(InfoBase(data.keyword, data.value))
        return infos


