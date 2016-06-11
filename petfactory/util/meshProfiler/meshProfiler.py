import maya.OpenMaya as om
import pprint
import sys
from PySide import QtGui, QtCore
import maya.OpenMayaUI as omui
from shiboken import wrapInstance

class BaseWin(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(BaseWin, self).__init__(parent) 

        self.setGeometry(200, 400, 300, 300)
        self.setWindowTitle('Test')
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.iconWidth = 50
        self.iconHeight = 18
        self.iconStrokeWidth = 1
        self.iconEdgeOffset = 4
        self.iconBgColor = QtGui.QColor(220, 220, 220, 0)
        self.iconActiveColor = QtGui.QColor(240, 170, 50, 255)

        # layout
        vbox = QtGui.QVBoxLayout(self)

        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Node', 'Triangles'])

        self.proxyModel = QtGui.QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        self.tableView = QtGui.QTableView()
        self.tableView.setModel(self.proxyModel)
        self.tableView.setSortingEnabled(True)

        header = self.tableView.horizontalHeader()
        header.setStretchLastSection(True)

        self.tableView.setModel(self.model)
        self.tableView.setIconSize(QtCore.QSize(self.iconWidth, self.iconHeight))
        vbox.addWidget(self.tableView)
        
        #self.populateTreeview('Roof 25%', .25, self.model)
        #self.populateTreeview('Door 50%', .50, self.model)
        #self.populateTreeview('Wheel 75%', .75, self.model)
        self.populateFromDict()

        self.tableView.setColumnWidth(0, 175)

    def populateFromDict(self):
        
        nodeName = '|root'
        
        
        mainDict = walkNode(nodeName)
        meshInfoDict = mainDict.get('infoDict')
        maxTris = mainDict.get('maxTris')
        
        for dagPath, infoDict in meshInfoDict.iteritems():
            
            uniqueName = infoDict.get('uniqueName')
            shortName = uniqueName.split('|')[-1]
            numTris = infoDict.get('numTris')
            
            self.populateTreeview(shortName, numTris, maxTris, self.model)
            
        
    def createIcon(self, vertValue):

        barWidth = vertValue * self.iconWidth

        pixmap = QtGui.QPixmap(self.iconWidth, self.iconHeight)
        pixmap.fill(self.iconBgColor)

        iconRect = QtCore.QRect(0, self.iconEdgeOffset, self.iconWidth-1, self.iconHeight-self.iconEdgeOffset*2)
        barRect = QtCore.QRect(0, self.iconEdgeOffset, barWidth-1, self.iconHeight-self.iconEdgeOffset*2)

        painter = QtGui.QPainter(pixmap)
        painter.fillRect(barRect, self.iconActiveColor)

        painter.setBrush(QtCore.Qt.NoBrush)
        pen = QtGui.QPen()
        pen.setBrush(self.iconActiveColor)
        pen.setWidth(self.iconStrokeWidth )
        painter.setPen(pen)
        painter.drawRect(iconRect)

        painter.end()
        return QtGui.QIcon(pixmap)

    def populateTreeview(self, name, numTris, maxTris, model):

        iconItem = QtGui.QStandardItem(name)
        iconItem.setSizeHint(QtCore.QSize(100, self.iconHeight))
        iconItem.setIcon(self.createIcon(numTris/float(maxTris)))
        
        numRows = model.rowCount()
        model.setItem(numRows, 0, iconItem)
        
        triNumItem = QtGui.QStandardItem()
        triNumItem.setData(numTris, QtCore.Qt.DisplayRole)
        model.setItem(numRows, 1, triNumItem)
        
        
        #parent.appendRow(item)

    
def walkDag(startObject):
    
    infoDict = {}
    mainDict = {'infoDict':infoDict}
    maxTris = 0
    
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
            numTris = triangleVertices.length()/3
            
            if numTris > maxTris:
                maxTris = numTris
                
            d = {   'uniqueName':mObj.partialPathName(),
                    'numVerts':fnMesh.numVertices(),
                    'numFaces':fnMesh.numPolygons(),
                    'numTris':numTris
                }
                    
            infoDict[mObj.fullPathName()] = d
       
        dagIter.next()
    
        mainDict['maxTris'] = maxTris
        
    return mainDict
    
    

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
    return infoDict


#walkNode('|root')
#walkSelected()


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

def show():
    win = BaseWin(parent=maya_main_window())
    win.show()
    
#show()

