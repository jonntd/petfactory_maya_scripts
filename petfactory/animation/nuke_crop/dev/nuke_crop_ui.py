from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui

import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
  
class RegexWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(RegexWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(200,100)
        self.setWindowTitle("Regex set")
        
        main_vbox = QtGui.QVBoxLayout()
        self.setLayout(main_vbox)
        
        self.x_min = simple_widget.add_spinbox(label='x min', parent_layout=main_vbox, min=-999, max=999, default=-1, double_spinbox=True, decimals=3)
        self.x_max = simple_widget.add_spinbox(label='x max', parent_layout=main_vbox, min=-999, max=999, default=1, double_spinbox=True, decimals=3)
        self.y_min = simple_widget.add_spinbox(label='y min', parent_layout=main_vbox, min=-999, max=999, default=-1, double_spinbox=True, decimals=3)
        self.y_max = simple_widget.add_spinbox(label='y max', parent_layout=main_vbox, min=-999, max=999, default=1, double_spinbox=True, decimals=3)
        self.z_offset = simple_widget.add_spinbox(label='z offset', parent_layout=main_vbox, min=-999, max=999, default=-3, double_spinbox=True, decimals=3)
        
        #simple_widget.add_spinbox(label='Frame Start', parent_layout=main_vbox, min=-999, max=9999, default=1)
        #simple_widget.add_spinbox(label='Frame End', parent_layout=main_vbox, min=-999, max=9999, default=1)
        
        main_vbox.addStretch()
        
        copy_button = QtGui.QPushButton('Copy to Nuke')
        main_vbox.addWidget(copy_button)
        
        copy_button.clicked.connect(self.copy_button_clicked)

    
    def copy_button_clicked(self):
        
        print(self.x_min.value())
        

def show():
    win = RegexWidget(parent=maya_main_window())
    win.show()


try:
    win.close()
    
except NameError:
    print('No win to close')
    
win = RegexWidget(parent=maya_main_window())
win.show()
win.move(100,250)