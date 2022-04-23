"""
This package is only used for creating DAG (Directed acyclic graph) node
in Maya representing parent child hierarchical relationship.

It is de-coupled from the data package, which solely represents the data
with in the ascii, in which may also include dag node data.

Example:

the following is an audio node

createNode audio -n "happy_frog";
	rename -uid "4D97ED00-45A7-3DF0-4531-63ACF0545B24";
	setAttr ".ef" 2188.9502562925172;
	setAttr ".se" 2188.9502562925172;
	setAttr ".f" -type "string" "C:/bgm/happy-frog.wav";

When presented as dag node, we are ignoring the detail node specific flags &
argument, we only care about the general information such as type, node name,
parent, size.

When presented as data object, we would categorize it as a node data object,
and more specifically an audio node data object, with audio path: 'C:/bgm/happy-frog.wav'
"""