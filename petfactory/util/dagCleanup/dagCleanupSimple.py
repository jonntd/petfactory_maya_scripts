import pymel.core as pm
from datetime import datetime
from PySide import QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken import wrapInstance
import os

def recurseDag(node, nodeSet, keepSet, parentList=[]):

    nodeSet.add(node)

    # if not visible, early return
    if not node.v.get():
        return

    childList = node.listRelatives(children=True)
    
    # leaf item
    if len(childList) == 0:

        if isinstance(node, pm.nodetypes.Mesh):
            [keepSet.add(n) for n in parentList]
            keepSet.add(node)


    # loop through the children
    else:
        for child in childList:  
            parentList.append(node)
            recurseDag(child, nodeSet, keepSet, parentList)

    if len(parentList) > 0:
        parentList.pop()

st = datetime.now()
nodeSet = set()
keepSet = set()
root = pm.PyNode('root')        
recurseDag(root, nodeSet, keepSet)
#diffSet = nodeSet.symmetric_difference(keepSet)
diffSet = nodeSet.difference(keepSet)
pm.select(diffSet)
et = datetime.now()
print 'Done in {} sec'.format((et-st).seconds)