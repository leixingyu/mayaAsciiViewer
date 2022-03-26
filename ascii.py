import maya.cmds as cmds

from pipelineUtil.fileSystem import winFile


class Ascii(winFile.WinFile):

    def __init__(self, path):
        super(Ascii, self).__init__(path)
        if self.ext != '.ma':
            raise TypeError('File {} is not an Maya Ascii type'.format(self.path))

        self._lineCount = 0

    def update(self):
        super(Ascii, self).update()
        self.update_line()

    def update_line(self):
        with open(self._path) as f:
            for count, _line in enumerate(f):
                pass
            self._lineCount = count

    def fopen(self):
        cmds.file(new=1, force=1)
        cmds.file(self.path, open=1)

    def fimport(self):
        cmds.file(self.path, i=1, usingNamespaces=0)
