from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
# popup win

class WebObjExportWidget(QtGui.QDialog):
    
    def __init__(self, parent=None):
        
        super(WebObjExportWidget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 300, 70)
        self.setWindowTitle("Web obj export")        
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        # add name         
        name_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(name_hbox)
        
        
        
        self.name_lineedit = QtGui.QLineEdit()
        name_hbox.addWidget(self.name_lineedit)
        
        add_name_btn = QtGui.QPushButton('Add Name')
        name_hbox.addWidget(add_name_btn)        
        add_name_btn.setMaximumWidth(70)
        add_name_btn.clicked.connect(self.add_name_btn_clicked)
        
        #self.name_combobox = QtGui.QComboBox()
        #name_hbox.addWidget(self.name_combobox)
        #self.name_combobox.addItems(['apa', 'katt'])
        
        # export 
        export_btn = QtGui.QPushButton('Export')
        vbox.addWidget(export_btn)
        export_btn.clicked.connect(self.export_btn_clicked) 
        #add_name_btn.setMaximumWidth(70)
        
        
        vbox.addStretch()   
        self.show()
        
    def add_name_btn_clicked(self):
        print(self.sender())
        
    def export_btn_clicked(self):
        print(self.sender())
        
        
        
def show():
    win = WebObjExportWidget(parent=maya_main_window())
    win.show()
    
show()