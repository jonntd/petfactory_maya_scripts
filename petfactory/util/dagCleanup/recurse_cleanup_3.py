import pymel.core as pm
from datetime import datetime

def recurseTreeView(node, nodeSet, keepSet, deleteSet):
    
    # if not visible, early return
    if not node.v.get():
        deleteSet.add(node)
        return
        
    nodeSet.add(node)
    
    childList = node.listRelatives(children=True)

    # leaf item
    if len(childList) == 0:

        if isinstance(node, pm.nodetypes.Mesh):

            while True:

                if node in keepSet:
                    break

                keepSet.add(node)
                
                parentList = node.listRelatives(parent=True)
                if len(parentList) > 0:
                    node = parentList[0]
                else:
                    break


    # loop through the children
    else:
        for child in childList:
            recurseTreeView(child, nodeSet, keepSet, deleteSet)
                

st = datetime.now()
root = pm.PyNode('root')
nodeSet = set()
keepSet = set()
deleteSet = set()
recurseTreeView(root, nodeSet, keepSet, deleteSet)
diffSet = nodeSet.difference(keepSet)
et = datetime.now()
#pm.select(diffSet)
print 'Done in {} sec'.format((et-st).seconds)
