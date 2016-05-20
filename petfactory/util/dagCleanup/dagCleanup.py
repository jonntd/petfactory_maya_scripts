import pymel.core as pm
from datetime import datetime
from PySide import QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken import wrapInstance
import os

   
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
        self.selectNodesCB.setChecked(True)
        vbox.addWidget(self.selectNodesCB)
        
        vbox.addStretch()
        
        cleanupButton = QtGui.QPushButton('Cleanup')
        cleanupButton.installEventFilter(self)
        cleanupButton.clicked.connect(self.cleanupButtonClicked)
        vbox.addWidget(cleanupButton)
        
        self.statusbar = QtGui.QStatusBar()
        vbox.addWidget(self.statusbar)
        
        self.statusbar.setSizeGripEnabled(False)
        
    def eventFilter(self, object, event):

        if event.type() == QtCore.QEvent.HoverEnter:
            self.statusbar.showMessage('May take several seconds')
            return True
            
        if event.type() == QtCore.QEvent.HoverLeave:
            #self.statusbar.clearMessage()
            return True
            
        return False
                
                
        
    def cleanup(self):
        
        selList = pm.ls(sl=True)
        if len(selList) < 1:
            print('Nothing is selected')
            return
            
        if not isinstance(selList[0], pm.nodetypes.Transform):
            print('Please select a transform')
            return
                          
        st = datetime.now()
        
        shapeDagSet = set()
        getValidNodes(selList[0], shapeDagSet, removeHidden=self.deleteHiddenCB.isChecked())
        
        deleteList = []
        deleteNotInSet(selList[0], shapeDagSet, deleteList)
        
        if self.selectNodesCB.isChecked():
            pm.select(deleteList)
            
        else:
            pm.delete(deleteList)
            
        et = datetime.now()
        self.statusbar.showMessage('Done in {} sec'.format((et-st).seconds))
    
    
    def cleanupButtonClicked(self):
        self.cleanup()

        
def show():
    win = MeasureWidget(parent=maya_main_window())
    win.show()
    
#show()
