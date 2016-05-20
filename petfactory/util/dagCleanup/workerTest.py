import pymel.core as pm
from datetime import datetime
from PySide import QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken import wrapInstance
import os, time
import maya.utils

       
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    

def doSphere( radius ):
    maya.cmds.sphere( radius=radius )
    
class Worker(QtCore.QThread):
    
    progress = QtCore.Signal(int)
    
    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.inc = 0
        
    def run(self):
        #print 'run from within worker'
        self.inc = 0
        self.timer.start(1000)
        
        self.exec_()

    def update(self):
        self.inc += 1
        self.progress.emit(self.inc)
        
        maya.utils.executeInMainThreadWithResult( doSphere, self.inc )
        
        if self.inc == 3:
            self.timer.stop()
            #self.timer.timeout.disconnect(self.update)
            #self.timer = None
            self.quit()
    
class MeasureWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(MeasureWidget, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 180, 100)
        self.setWindowTitle('DAG Cleanup')
        
        self.worker = Worker()
        self.worker.progress.connect(self.cleanupProgress)
        self.worker.finished.connect(self.workerFinished)
        
        vbox = QtGui.QVBoxLayout(self)
        
        self.label = QtGui.QLabel('')
        vbox.addWidget(self.label)
        
        cleanupButton = QtGui.QPushButton('Cleanup')
        cleanupButton.clicked.connect(self.cleanupButtonClicked)
        vbox.addWidget(cleanupButton)
        
    def cleanupButtonClicked(self):
        self.label.setText('Processing')
        self.worker.start()
        
    def cleanupProgress(self, val):
        print 'Value from outside: {}'.format(val)
        self.label.setText('Processing{}'.format(val%4*'.'))
        
    def workerFinished(self):
        self.label.setText('Cleanup Done!')
        
        
def show():
    win = MeasureWidget(parent=maya_main_window())
    win.show()
    
show()


