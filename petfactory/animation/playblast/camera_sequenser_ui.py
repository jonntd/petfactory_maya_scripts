from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import re
import pymel.core as pm

import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

import petfactory.animation.playblast.camera_sequenser as camera_sequenser
reload(camera_sequenser)

import petfactory.util.verify as pet_verify
reload(pet_verify)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
  
class CameraSequenserWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(CameraSequenserWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        

        # layout
        content_layout = QtGui.QVBoxLayout()
        self.setLayout(content_layout)
  
        
        self.resize(300,100)
        self.setWindowTitle("Camera sequenser")

        
        # rig group box
        current_shot_groupbox = QtGui.QGroupBox("Current shot")
        content_layout.addWidget(current_shot_groupbox)
        current_shot_groupbox_vbox = QtGui.QVBoxLayout()
        current_shot_groupbox.setLayout(current_shot_groupbox_vbox)
        
        self.current_shot_label = QtGui.QLabel('')
        current_shot_groupbox_vbox.addWidget(self.current_shot_label)
        
        set_current_shot_button = QtGui.QPushButton('Set current shot')
        set_current_shot_button.clicked.connect(self.set_current_shot_clicked)
        current_shot_groupbox_vbox.addWidget(set_current_shot_button)
        
        self.nodetype_combobox = simple_widget.labeled_combobox(label='Add shot', parent_layout=content_layout, items=['after current shot', 'at current time'])
        
        
        content_layout.addStretch()
        
        create_shot_button = QtGui.QPushButton('Create shot')
        create_shot_button.clicked.connect(self.create_shot_clicked)
        content_layout.addWidget(create_shot_button)
        
        self.current_shot = None
    
    def create_shot_clicked(self):
                
        if not pet_verify.verify_string(self.current_shot_label.text(), pm.nodetypes.Shot):
            
            self.current_shot = None
            self.current_shot_label.setText('None')
        
        shot = None
        
        if self.nodetype_combobox.currentIndex() == 0:
            shot = camera_sequenser.create_shot_from_timerange(current_shot=self.current_shot)

        elif self.nodetype_combobox.currentIndex() == 1:
            shot = camera_sequenser.create_shot_from_timerange()
            
        if shot is not None:
            self.current_shot = shot
            self.current_shot_label.setText(shot.name())
            
            
    def set_current_shot_clicked(self):
        
        if pet_verify.verify_selection(pm.nodetypes.Shot):
            
            self.current_shot = pm.ls(sl=True)[0]
            self.current_shot_label.setText(self.current_shot.name())


def show():
    win = CameraSequenserWidget(parent=maya_main_window())
    win.show()
    return win

'''
try:
    win.close()
    
except NameError:
    print('No win to close')
    
win = show()
win.move(100,150)
'''
