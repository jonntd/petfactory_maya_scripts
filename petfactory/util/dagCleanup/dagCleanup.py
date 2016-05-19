import pymel.core as pm
from datetime import datetime
from PySide import QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken import wrapInstance

   
def getValidNodes(node, shapeDagSet, removeHidden):
    '''find all children of node that are meshes and add their parent dag nodes to shapeDagSet'''
    
    childList = node.listRelatives(children=True)

    # leafnode case
    if len(childList) == 0:
        if isinstance(node, pm.nodetypes.Mesh):
            
            shapeDagSet.add(node) # add the starting node
    
            while True:
                parentList = node.listRelatives(parent=True)
                if len(parentList) > 0:
                    node = parentList[0]
                    
                    if node in shapeDagSet:
                        break
                        
                    shapeDagSet.add(node)
                    
                else:
                    break
                    
    # recurse  the children
    else:               
        for child in childList:
            if removeHidden:
                if not child.v.get(): # skip non visible
                    continue
                
            getValidNodes(child, shapeDagSet, removeHidden)


def deleteNotInSet(node, shapeDagSet, deleteList):
    '''Gather all the nodes that are empty and that we can delete'''
    
    childList = node.listRelatives(children=True)
    
    if node not in shapeDagSet:
        deleteList.append(node)
        return
                
    # recurse  the children
    for child in childList:    
        deleteNotInSet(child, shapeDagSet, deleteList)


def cleanup(root, removeHidden, selectNodes):

    st = datetime.now()
    shapeDagSet = set()
    getValidNodes(root, shapeDagSet, removeHidden)
    deleteList = []
    deleteNotInSet(root, shapeDagSet, deleteList)
    if selectNodes:
        pm.select(deleteList)
    else:
        pm.delete(deleteList)
    et = datetime.now()
    print 'The hierarchy cleanup took: {} seconds'.format((et-st).seconds)
    

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
              
class MeasureWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(MeasureWidget, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 180, 100)
        self.setWindowTitle('DAG Cleanup')
        
        vbox = QtGui.QVBoxLayout(self)
        
        self.deleteHiddenCB = QtGui.QCheckBox('Delete Hidden')
        vbox.addWidget(self.deleteHiddenCB)
        
        self.selectNodesCB = QtGui.QCheckBox('Select Nodes to delete')
        vbox.addWidget(self.selectNodesCB)
        
        vbox.addStretch()
        cleanupButton = QtGui.QPushButton('Cleanup')
        cleanupButton.clicked.connect(self.cleanupButtonClicked)
        vbox.addWidget(cleanupButton)

    def cleanupButtonClicked(self):

        selList = pm.ls(sl=True)
        if len(selList) < 1:
            print('Nothing is selected!')
            return
        
        
        cleanup(selList[0],
                removeHidden=self.deleteHiddenCB.isChecked(),
                selectNodes=self.selectNodesCB.isChecked())
        
        
def show():
    win = MeasureWidget(parent=maya_main_window())
    win.show()
    
show()


