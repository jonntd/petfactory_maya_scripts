import maya.OpenMaya as om
import pprint


def walkDag(startObject):
    
    infoDict = {}
    dagIter = om.MItDag(om.MItDag.kBreadthFirst)
    #dagIter = om.MItDag(om.MItDag.kDepthFirst)
    dagIter.reset(startObject)

    while not dagIter.isDone():
    
        mObj = om.MDagPath()
        dagIter.getPath(mObj)
    
        if mObj.apiType() == om.MFn.kMesh:
            
            fnMesh = om.MFnMesh(mObj)
                        
            triangleCounts = om.MIntArray()
            triangleVertices = om.MIntArray()
            fnMesh.getTriangles(triangleCounts, triangleVertices)
            
            d = {   'uniqueName':mObj.partialPathName(),
                    'numVerts':fnMesh.numVertices(),
                    'numFaces':fnMesh.numPolygons(),
                    'numTris':triangleVertices.length()/3
                }
                    
            infoDict[mObj.fullPathName()] = d
       
        dagIter.next()
    
    return infoDict
    
    

def walkSelected():
    
    selList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selList);

    if selList.isEmpty():
        print 'nothing is selected'
        return
    
    startObject = om.MDagPath()
    selList.getDagPath(0, startObject)
    infoDict = walkDag(startObject)
    pprint.pprint(infoDict)


def walkNode(nodeName):
    
    selList = om.MSelectionList()
    startObject = om.MDagPath()
    selList.add(nodeName)
    selList.getDagPath(0, startObject)
    infoDict = walkDag(startObject)
    pprint.pprint(infoDict)


walkNode('|root')
#walkSelected()



