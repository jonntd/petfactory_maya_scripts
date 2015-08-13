from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui



def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
  
class RegexWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(RegexWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        
        self.resize(200,100)
        self.setWindowTitle("Regex set")
        


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