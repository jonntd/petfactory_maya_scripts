from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
class Test(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(Test, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 180, 100)
        #self.setWindowTitle('Measure')
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        self.btn = QtGui.QPushButton('Button')
        vbox.addWidget(self.btn)        

        self.menu = QtGui.QMenu(self)
        self.btn.setMenu(self.menu)
        self.num_colors = 100
        self.current_color_index = 0
                
        for i in range(self.num_colors ):
            self.add_menu_items(self.menu, i)
                       
        self.select_color(self.current_color_index)
            
        vbox.addStretch()
        
    def add_menu_items(self, menu, color_index):
        
        color = QtGui.QColor()
        c = color_index / float(self.num_colors)
        color.setRgbF(c,c,c)
        pixmap = QtGui.QPixmap(50, 50)
        pixmap.fill(QtGui.QColor(color))
        icon = QtGui.QIcon(pixmap)
                
        action = QtGui.QAction(icon, str(color_index), self)
        action.triggered.connect(partial(self.select_color, color_index))
        
        menu.addAction(action)

        
    def select_color(self, color_index):
        
        color = QtGui.QColor()
        c = color_index / float(self.num_colors)
        color.setRgbF(c,c,c)
        pixmap = QtGui.QPixmap(50, 50)
        pixmap.fill(QtGui.QColor(color))
        icon = QtGui.QIcon(pixmap)
        
        self.btn.setIcon(icon)
        self.btn.setIconSize(QtCore.QSize(10,10))
        #self.btn.setText('({}) set color'.format(color_index))
        self.btn.setText('set color')
             
def show():
    win = Test(parent=maya_main_window())
    win.show()
show()