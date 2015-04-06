from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial

import petfactory.gui.simple_widget as simple_widget

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
  
class PlayblastWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(PlayblastWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        # main layout
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)
        
        # menu bar
        self.menu_bar = QtGui.QMenuBar()
        self.main_layout.addWidget(self.menu_bar)
        
        # add menu
        self.file_menu = self.menu_bar.addMenu('File')
        
        # add sub menus
        self.save_clips_action = QtGui.QAction('Save clips', self)
        self.save_clips_action.triggered.connect(self.save_clips_action_triggered)
        self.file_menu.addAction(self.save_clips_action)
        
        self.load_clips_action = QtGui.QAction('Load clips', self)
        self.load_clips_action.triggered.connect(self.load_clips_action_triggered)
        self.file_menu.addAction(self.load_clips_action)
        
        # content layout
        self.content_layout = QtGui.QVBoxLayout()
        self.content_layout.setContentsMargins(7,7,7,7)
        self.main_layout.addLayout(self.content_layout)
        
        
        # -----------------------------------------------------------------------
        

        # tableview
        self.clip_tableview = QtGui.QTableView()
        self.content_layout.addWidget(self.clip_tableview)
        
        self.resolution_dict = {'1920 x 1080':(1920, 1080),
                                '1280 x 720':(1280, 720),
                                '960 x 540':(960, 540)}
                                
        resolution_keys = self.resolution_dict.keys()
        resolution_keys.sort()
        
        # resolution
        self.resolution_combobox = simple_widget.labeled_combobox(label='Resolution', parent_layout=self.content_layout, items=resolution_keys)
        
        
    
    def save_clips_action_triggered(self):
        print(self.sender())
        
    
    def load_clips_action_triggered(self):
        print(self.sender())


def show():
    win = PlayblastWidget(parent=maya_main_window())
    win.show()

try:
    win.close()
    
except NameError:
    pass 
    
win = PlayblastWidget(parent=maya_main_window())
win.show()
win.move(100,150)