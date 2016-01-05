from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
              
class ListAttrUI(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(ListAttrUI, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 200, 400)
        self.setWindowTitle('Measure')
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        self.tableview = QtGui.QTableView()
        vbox.addWidget(self.tableview)
        
        self.model = QtGui.QStandardItemModel()
        self.tableview.setModel(self.model)
        self.tableview.horizontalHeader().setStretchLastSection(True)
        self.model.setHorizontalHeaderLabels(['attr', 'value'])
        
        btn = QtGui.QPushButton('Refresh')
        vbox.addWidget(btn)
        btn.clicked.connect(self.refresh_btn_clicked)
        #vbox.addStretch()
                
    def refresh_btn_clicked(self):
        
        sel_list = pm.ls(sl=True)
        
        if len(sel_list) < 1:
            pm.warning('Nothing is selected')
            return
            
        node = sel_list = pm.ls(sl=True)[0]
        attr_list = node.listAttr(userDefined=True, settable=True)  
        
        if len(attr_list) < 1:
            pm.warning('No attrs found')
            return
            
        self.add_items(attr_list)
        
        
    def add_items(self, attr_list):        
        
        num_rows = self.model.rowCount()
        
        for row in range(num_rows):
            self.model.removeRow(0)
        
        for attr in attr_list:
            
            if attr.isChild():
                print('skipping: {}'.format(attr))
                continue

            attr_name = attr.name(includeNode=False)                
            attr_type = attr.type()
            attr_value = attr.get()
            
            # attr name            
            attr_item = QtGui.QStandardItem(attr_name)
            
            # attr value
            value_item = QtGui.QStandardItem()
            value_item.setData(attr_value, QtCore.Qt.EditRole)
            
            
            self.model.appendRow([attr_item, value_item])
             
def show():
    win = ListAttrUI(parent=maya_main_window())
    win.show()

show()