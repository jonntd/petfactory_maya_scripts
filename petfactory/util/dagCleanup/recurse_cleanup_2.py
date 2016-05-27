def getValidNodes(node, keepSet):
    '''find all children of node that are meshes and add their parent dag nodes to shapeDagSet'''
    
    childList = node.listRelatives(children=True)

    # leafnode case
    if len(childList) == 0:
        if isinstance(node, pm.nodetypes.Mesh):
            
            keepSet.add(node) # add the starting node
    
            while True:
                parentList = node.listRelatives(parent=True)
                
                if len(parentList) > 0:
                    node = parentList[0]
                    
                    if node in keepSet:
                        break
                        
                    keepSet.add(node)
                    
                else:
                    break
                    
    # recurse  the children
    else:               
        for child in childList:
            if not child.v.get(): # skip non visible
                continue
                
            getValidNodes(child, keepSet)


def deleteNotInSet(node, keepSet, deleteList):
    '''Gather all the nodes that are empty and that we can delete'''
    
    childList = node.listRelatives(children=True)
    
    if node not in keepSet:
        deleteList.append(node)
        return
                
    # recurse  the children
    for child in childList: 
        deleteNotInSet(child, keepSet, deleteList)
        
st = datetime.now()
root = pm.PyNode('root')        
keepSet = set()
getValidNodes(root, keepSet)

deleteList = []
deleteNotInSet(root, keepSet, deleteList)

#pm.select(deleteList)

et = datetime.now()
print 'Done in {} sec'.format((et-st).seconds)
