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
        
        self.valid_attr = ['double', 'long', 'bool']
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        self.tableview = QtGui.QTableView()
        vbox.addWidget(self.tableview)
        
        self.model = QtGui.QStandardItemModel()
        self.tableview.setModel(self.model)
        self.tableview.horizontalHeader().setStretchLastSection(True)
        self.model.setHorizontalHeaderLabels(['attr', 'value'])
        
        btn_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(btn_hbox)
        
        # copy attr
        copy_btn = QtGui.QPushButton('Copy')
        btn_hbox.addWidget(copy_btn )
        copy_btn.clicked.connect(self.copy_btn_clicked)
        
        # paste attr
        paste_btn = QtGui.QPushButton('Paste')
        btn_hbox.addWidget(paste_btn)
        paste_btn.clicked.connect(self.paste_btn_clicked)
        
        #vbox.addStretch()
    
    def paste_btn_clicked(self):
        
        sel_list = pm.ls(sl=True)
        
        if len(sel_list) < 1:
            pm.warning('Nothing is selected')
            return
            
        num_rows = self.model.rowCount()
        
        for sel in sel_list:
            
            for row in range(num_rows):
                
                attr_item = self.model.item(row, 0)
                
                if attr_item.checkState() == QtCore.Qt.CheckState.Unchecked:
                    continue
                    
                attr = self.model.item(row, 0).data(role=QtCore.Qt.EditRole)
                value = self.model.item(row, 1).data(role=QtCore.Qt.EditRole)
                pm.setAttr('{}.{}'.format(sel, attr), value)

                      
    def copy_btn_clicked(self):
        
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
                print('Compound attr. skipping attr: {} of type: {}'.format(attr_name, attr_type))
                continue

            attr_type = attr.type()
            attr_name = attr.name(includeNode=False)
            #print(attr_type)
            
            if attr_type not in self.valid_attr:
                print('skipping attr: {} of type: {}'.format(attr_name, attr_type))
                continue
                            
            attr_value = attr.get()
            
            # attr name            
            attr_item = QtGui.QStandardItem(attr_name)
            attr_item.setCheckable(True)
            attr_item.setCheckState(QtCore.Qt.CheckState.Checked)
            
            # attr value
            value_item = QtGui.QStandardItem()
            value_item.setData(attr_value, QtCore.Qt.EditRole)
            
            
            self.model.appendRow([attr_item, value_item])
             
def show():
    win = ListAttrUI(parent=maya_main_window())
    win.show()

show()