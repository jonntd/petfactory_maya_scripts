from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)


def connect_selected_crv(crv_xfo, canvas_node):
    
    crv_shape = crv_xfo.getShape()
    crv_cvs = crv_shape.getCVs()
    
    canvas_node.profileCount.set(len(crv_cvs))
    
    for index, cv in enumerate(crv_cvs):
        crv_shape.controlPoints[index] >> canvas_node.profile[index]
        
        

def remove_input_crv(canvas_node):
    
    num = canvas_node.profile.numElements()
    
    for i in range(num):
        if canvas_node.profile[i].isConnected():
           canvas_node.profile[i].disconnect()
           
    canvas_node.profileCount.set(0)
    
    
    
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
       
class Panel(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(Panel, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 250, 100)
        self.setWindowTitle('Panel')
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        self.canvas_lineedit = simple_widget.add_filtered_populate_lineedit(label='  canvasNode >>  ', parent_layout=vbox, nodetype=pm.nodetypes.CanvasNode)
        
        # connect
        
        connect_cvs_btn = QtGui.QPushButton('Connect CVs to profile')
        vbox.addWidget(connect_cvs_btn)
        connect_cvs_btn.clicked.connect(self.connect_cvs_btn_clicked)
        
        p = connect_cvs_btn.palette()
        p.setColor(connect_cvs_btn.backgroundRole(), QtGui.QColor(0,100,0))
        connect_cvs_btn.setPalette(p)

        # break
        
        break_con_btn = QtGui.QPushButton('Break connection')
        vbox.addWidget(break_con_btn)
        break_con_btn.clicked.connect(self.break_con_btn_clicked)
        
        p = break_con_btn.palette()
        p.setColor(break_con_btn.backgroundRole(), QtGui.QColor(100,0,0))
        break_con_btn.setPalette(p)
           
        
        vbox.addStretch()
        
    def break_con_btn_clicked(self):
        
        canvas_node = pm.PyNode(self.canvas_lineedit.text())
        remove_input_crv(canvas_node)

        
    def connect_cvs_btn_clicked(self):
        
        canvas_node = pm.PyNode(self.canvas_lineedit.text())
        crv_xfo = pm.ls(sl=True)[0]
        connect_selected_crv(crv_xfo, canvas_node)
        
        

def show():
    win = Panel(parent=maya_main_window())
    win.show()
    
    
show()