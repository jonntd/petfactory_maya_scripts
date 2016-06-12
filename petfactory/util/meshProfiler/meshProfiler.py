import maya.OpenMaya as om
import pprint
import sys
from PySide import QtGui, QtCore
import maya.OpenMayaUI as omui
from shiboken import wrapInstance
from functools import partial
import pymel.core as pm


class TableView(QtGui.QTableView):
    
    def __init__(self, *args, **kwargs):
        super(TableView, self).__init__(*args, **kwargs)

    def contextMenuEvent(self, event):

        row = self.rowAt(event.pos().y())

        if row < 0:
            return

        item = self.model().item(row)
        dagPath = item.data(QtCore.Qt.UserRole+1)

        self.menu = QtGui.QMenu(self)
        renameAction = QtGui.QAction('Select Node', self)
        renameAction.triggered.connect(partial(self.selectNode, dagPath))
        self.menu.addAction(renameAction)
        self.menu.popup(QtGui.QCursor.pos())

    def selectNode(self, name):
        pm.select(name)
        
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
        self.iconBgColor = QtGui.QColor(0, 0, 0, 0)
        self.barFrameColor = QtGui.QColor(100, 100, 100, 255)
        self.iconActiveColor = QtGui.QColor(240, 170, 50, 255)

        self.highColor = QtGui.QColor(219, 148, 86, 255)
        self.lowColor = QtGui.QColor(88, 165, 204, 255)
        self.midColor = QtGui.QColor(85, 171, 100, 255)

        # layout
        vbox = QtGui.QVBoxLayout(self)

        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Node', 'Triangles'])

        self.proxyModel = QtGui.QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        #self.tableView = QtGui.QTableView()
        self.tableView = TableView()
        self.tableView.setModel(self.proxyModel)
        self.tableView.setSortingEnabled(True)

        header = self.tableView.horizontalHeader()
        header.setStretchLastSection(True)

        self.tableView.setModel(self.model)
        self.tableView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.tableView.setIconSize(QtCore.QSize(self.iconWidth, self.iconHeight))
        vbox.addWidget(self.tableView)
        
        self.populateFromDict()
        self.tableView.setColumnWidth(0, 175)

        setVisibilityButton = QtGui.QPushButton('Set Visibility')
        vbox.addWidget(setVisibilityButton)
        setVisibilityButton.clicked.connect(self.setVisibilityButtonClicked)

        self.visCheckBox = QtGui.QCheckBox('Visibility')
        vbox.addWidget(self.visCheckBox)

    def setVisibilityButtonClicked(self):
        
        nameList = []
        selectedIndexes = self.tableView.selectionModel().selectedRows()
        for index in selectedIndexes:
            nameList.append(self.model.item(index.row()).data(QtCore.Qt.UserRole+1))

        setVisibility(nameList, self.visCheckBox.isChecked())

    def populateFromDict(self):
        
        nodeName = '|root'
        
        mainDict = walkNode(nodeName)
        meshInfoDict = mainDict.get('infoDict')
        maxTris = mainDict.get('maxTris')
        
        for dagPath, infoDict in meshInfoDict.iteritems():
            
            uniqueName = infoDict.get('uniqueName')
            numTris = infoDict.get('numTris')
            self.populateTreeview(dagPath, uniqueName, numTris, maxTris, self.model)
            
        
    def createIcon(self, vertValue):

        barWidth = vertValue * self.iconWidth

        pixmap = QtGui.QPixmap(self.iconWidth, self.iconHeight)


        pixmap.fill(self.iconBgColor)

        iconRect = QtCore.QRect(0, self.iconEdgeOffset, self.iconWidth-1, self.iconHeight-self.iconEdgeOffset*2)
        barRect = QtCore.QRect(0, self.iconEdgeOffset, barWidth-1, self.iconHeight-self.iconEdgeOffset*2)

        painter = QtGui.QPainter(pixmap)

        if vertValue > .9:
            color = self.highColor

        elif vertValue > .75:
            color = self.midColor

        else:
            color = self.lowColor

        painter.fillRect(barRect, color)

        painter.setBrush(QtCore.Qt.NoBrush)
        pen = QtGui.QPen()
        pen.setBrush(self.barFrameColor)
        pen.setWidth(self.iconStrokeWidth )
        painter.setPen(pen)
        painter.drawRect(iconRect)

        painter.end()
        return QtGui.QIcon(pixmap)

    def populateTreeview(self, dagPath, uniqueName, numTris, maxTris, model):

        name = uniqueName.split('|')[-1]
        iconItem = QtGui.QStandardItem(name)
        iconItem.setToolTip(uniqueName)

        iconItem.setData(dagPath, QtCore.Qt.UserRole+1)
        iconItem.setSizeHint(QtCore.QSize(100, self.iconHeight))
        iconItem.setIcon(self.createIcon(numTris/float(maxTris)))
        iconItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        
        numRows = model.rowCount()
        model.setItem(numRows, 0, iconItem)
        
        triNumItem = QtGui.QStandardItem()
        triNumItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
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
    
    
def setVisibility(nameList, visible=True):
    
    selList = om.MSelectionList()
    
    for name in nameList:
        selList.add(name)
        
    selIter = om.MItSelectionList(selList)
       
    mObj = om.MObject()
    while not selIter.isDone():
        selIter.getDependNode(mObj)
        depFn = om.MFnDependencyNode(mObj)
        try:
            plug = depFn.findPlug('visibility')
            plug.setBool(visible)
            #plugAttr = plug.attribute()      
            #if om.MFnNumericAttribute(plugAttr).unitType() == om.MFnNumericData.kBoolean:
            #    plug.setBool(visible)
            
        except:
            om.MGlobal.displayError('Could not set the attribute.')

        selIter.next()
        

def walkSelected():
    
    selList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selList);

    if selList.isEmpty():
        print 'nothing is selected'
        return
    
    startObject = om.MDagPath()
    selList.getDagPath(0, startObject)
    infoDict = walkDag(startObject)
    #pprint.pprint(infoDict)


def walkNode(nodeName):
    
    selList = om.MSelectionList()
    startObject = om.MDagPath()
    selList.add(nodeName)
    selList.getDagPath(0, startObject)
    infoDict = walkDag(startObject)
    #pprint.pprint(infoDict)
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

