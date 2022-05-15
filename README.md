# Maya Ascii Viewer

Maya Ascii file (.ma) standalone viewer, acquire essential file information
and visualize data without needing to wait for Maya to open.

![preview](https://i.imgur.com/HFitkdR.png)

## Getting Started

Download the executable directly [here](https://github.com/leixingyu/mayaAsciiViewer/releases/tag/v1.0.0), built with [Pyinstaller](https://pyinstaller.org/en/stable/)

OR.

Download the source code and install all the [dependencies](#dependencies)

```
python asciiViewer.py
```

### Scripting

Basic parsing

```python
mfile = r'C:/example.ma'

loader = Loader()
blocks = loader.load(mfile)
```

```python
>> len(blocks)  # number of top level maya objects parsed
--------------
4983  
```

```python
>> blocks[-1].index  # the last ascii block is at line 52223
--------------
52223 

>> blocks[-1].desc  # short description of the block
--------------
createNode animCurveUA -n "Right_MidFing_02_Pose_rotateY";

>> blocks[-1].asc.read_detail(52223)  # full description
--------------
createNode animCurveUA -n "Right_MidFing_02_Pose_rotateY";
	rename -uid "693A6E85-4839-D09B-8886-7096150EC40C";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -5 0.018 0 0 10 2.926;
```

Detail parsing:
```python
>> blocks[-2].__class__  # type of the block, a.k.a the mel command type
--------------
<class 'asciiBlock.ConnectionBlock'>

>> blocks[-2].source  # source attribute of the connection object
--------------
ikRPsolver.msg
```

```python
>> audios = Audio.from_blocks(blocks)  # parse audio node
>> audios[0].path
--------------
C:/bgm/happy-frog.wav

>> audios[0].offset
--------------
0
```

```python
>> refs = Reference.from_blocks(blocks)  # parse reference node
>> refs[0].path
--------------
C:/test.ma

>> refs[0].refnode
--------------
testRN
```

## Dependencies

- [Qt](https://github.com/mottosso/Qt.py): a module that supports different
python qt bindings
    ```
    pip install Qt.py
    ```

- [PyQtChart](https://pypi.org/project/PyQtChart/): an add-on module for Qt
for creating charts (Need to check compatibility with your current Qt install,
most likely you'll want to use Python 3, since PyQtChart is added after Qt 5.7)
    ```
    pip install PyQtChart
    ```

- [qt-material **[Optional]**](https://github.com/UN-GCPDS/qt-material): a
material inspired stylesheet for PySide2, PySide6, PyQt5 and PyQt6 
  ```
  pip install qt-material
  ```

- [guiUtil](https://github.com/leixingyu/guiUtil):
my gui library for some handy qt templates.
