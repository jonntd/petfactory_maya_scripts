from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import re
import pymel.core as pm

import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

import petfactory.util.verify as pet_verify
reload(pet_verify)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
  
class CreateCurveJointsWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(CreateCurveJointsWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.active_set = None
        
        self.resize(300,100)
        self.setWindowTitle("Create curve joints")
        
        # layout
        main_layout = QtGui.QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout)
        
        '''
        self.menu_bar = QtGui.QMenuBar()
        main_layout.addWidget(self.menu_bar)
        file_menu = self.menu_bar.addMenu('File')
        
        self.set_active_action = QtGui.QAction('Active set (None)', self)
        self.set_active_action.triggered.connect(self.set_active_set)
        file_menu.addAction(self.set_active_action)
        
        
        set_action = QtGui.QAction('Remove from Set', self)
        set_action.triggered.connect(self.remove_from_set)
        file_menu.addAction(set_action)
        '''
        
        
        
        # layout
        content_layout = QtGui.QVBoxLayout()
        content_layout.setContentsMargins(7,7,7,7)
        main_layout.addLayout(content_layout)
        
        self.curve_lineedit = simple_widget.add_filtered_populate_lineedit(label='Add curve >', parent_layout=content_layout, nodetype=pm.nodetypes.NurbsCurve)

        self.number_of_joints_spinbox = simple_widget.add_spinbox(label='Number of joints', parent_layout=content_layout, min=2, max=99, default=4)


        content_layout.addStretch()
        
        
        create_joints_button = QtGui.QPushButton('Create joints')
        create_joints_button.clicked.connect(self.create_joints_button_clicked)
        content_layout.addWidget(create_joints_button)
    
    def create_joints_button_clicked(self):        
        curve_unicoide = self.curve_lineedit.text()
        
        curve_node = pet_verify.to_pynode(curve_unicoide)
        num_joints = self.number_of_joints_spinbox.value()
        
        if curve_node is None:
            pm.warning('Not a valid curve')
            return
            
        print(curve_node, num_joints)
                    
        
                                            
def show():
    win = CreateCurveJointsWidget(parent=maya_main_window())
    win.show()
    return win

'''
try:
    win.close()
    
except NameError:
    pass
    
win = show()
win.move(100,150)
'''