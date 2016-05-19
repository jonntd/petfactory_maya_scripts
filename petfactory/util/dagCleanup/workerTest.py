import pymel.core as pm
from datetime import datetime
from PySide import QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken import wrapInstance
import os, time

       
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
 
class Worker(QtCore.QThread):
    
    cleanupProgress = QtCore.Signal(int)
    cleanupDone = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.timer = QtCore.QTimer(self)
        self.inc = 0
        
    def run(self):
        print 'run from within worker'
                   
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

        
    def update(self):
        self.inc += 1
        self.cleanupProgress.emit(self.inc)
        
        if self.inc == 5:
            self.timer.stop()
            self.cleanupDone.emit()
    
class MeasureWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(MeasureWidget, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 180, 100)
        self.setWindowTitle('DAG Cleanup')
        
        self.worker = Worker()
        self.worker.cleanupProgress.connect(self.cleanupProgress)
        self.worker.cleanupDone.connect(self.cleanupDone)
        
        vbox = QtGui.QVBoxLayout(self)
        
        self.label = QtGui.QLabel('Test')
        vbox.addWidget(self.label)
        
        cleanupButton = QtGui.QPushButton('Cleanup')
        cleanupButton.clicked.connect(self.cleanupButtonClicked)
        vbox.addWidget(cleanupButton)
        
    def cleanupButtonClicked(self):
        self.worker.start()
        
    def cleanupProgress(self, val):
        print 'Value from outside: {}'.format(val)
        self.label.setText('Processing{}'.format(val%4*'.'))
        
    def cleanupDone(self):
        self.label.setText('Cleanup Done!')
        
        
def show():
    win = MeasureWidget(parent=maya_main_window())
    win.show()
    
show()


