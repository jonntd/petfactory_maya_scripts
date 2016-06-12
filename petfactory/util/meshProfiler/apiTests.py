import maya.OpenMaya as om

    
def walkDag(startObject):
    
    dagIter = om.MItDag(om.MItDag.kBreadthFirst)
    dagIter.reset(startObject)
    
    mDagPath = om.MDagPath()
    while not dagIter.isDone():

        dagIter.getPath(mDagPath)
        
        if mDagPath.apiType() == om.MFn.kMesh:
            
            fnMesh = om.MFnMesh(mDagPath)
            parentMobj = fnMesh.parent(0)
            fnDependNode = om.MFnDependencyNode(parentMobj)
            fnDagNode = om.MFnDagNode(parentMobj)
            
            print fnDependNode.name()
            print fnDagNode.fullPathName()
            
        dagIter.next()


selList = om.MSelectionList()
startObject = om.MDagPath()
selList.add('root')
selList.getDagPath(0, startObject)

walkDag(startObject)