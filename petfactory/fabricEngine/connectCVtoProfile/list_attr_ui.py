from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
              
class MeasureWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(MeasureWidget, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 200, 400)
        self.setWindowTitle('Measure')
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        self.tableview = QtGui.QTableView()
        vbox.addWidget(self.tableview)
        
        self.model = QtGui.QStandardItemModel()
        self.tableview.setModel(self.model)
        
        btn = QtGui.QPushButton('Refresh')
        vbox.addWidget(btn)
        btn.clicked.connect(self.refresh_btn_clicked)
        #vbox.addStretch()
        #self.add_items()
        
    def refresh_btn_clicked(self):
        
        self.add_items() 
        
    def add_items(self):        
        
        num_rows = self.model.rowCount()
        
        for row in range(num_rows):
            self.model.removeRow(0)
        
        node = sel_list = pm.ls(sl=True)[0]
        user_defined_attr = node.listAttr(userDefined=True, settable=True)               
    
        for attr in user_defined_attr:
            
            if attr.isChild():
                print('skipping: {}'.format(attr))
                continue
                
            self.model.appendRow(QtGui.QStandardItem(attr.name(includeNode=False)))
             
def show():
    win = MeasureWidget(parent=maya_main_window())
    win.show()

show()