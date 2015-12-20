from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)


def connect_selected_crv(crv_xfo, canvas_node):
    
    try:
        crv_shape = crv_xfo.getShape()
        crv_cvs = crv_shape.getCVs()
    
    except AttributeError as e:
        pm.warning('{}'.format(e))
        return
        
    
    try:
        canvas_node.sideProfileCount.set(len(crv_cvs))
        
        for index, cv in enumerate(crv_cvs):
            crv_shape.controlPoints[index] >> canvas_node.sideProfile[index]
            
    except AttributeError as e:
        pm.warning('{}'.format(e))
        
        

def remove_input_crv(canvas_node):
    
    try: 
        num = canvas_node.sideProfile.numElements()
    
        for i in range(num):
            if canvas_node.sideProfile[i].isConnected():
               canvas_node.sideProfile[i].disconnect()
               
        canvas_node.sideProfileCount.set(0)
        
    except AttributeError as e:
        pm.warning('{}'.format(e))
    
    
    
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
       
class Panel(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(Panel, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 250, 100)
        self.setWindowTitle('TwoCircleTangent')
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        # create canvas node
        create_canvas_node_btn = QtGui.QPushButton('Create canvas node')
        vbox.addWidget(create_canvas_node_btn)
        create_canvas_node_btn.clicked.connect(self.create_canvas_node_btn_clicked)
        
        
        # canvas node lineedit
        self.canvas_lineedit = simple_widget.add_filtered_populate_lineedit(label='  canvasNode >>  ', parent_layout=vbox, nodetype=pm.nodetypes.CanvasNode)
           
                
        # connect        
        connect_cvs_btn = QtGui.QPushButton('Connect CVs to profile')
        vbox.addWidget(connect_cvs_btn)
        connect_cvs_btn.clicked.connect(self.connect_cvs_btn_clicked)
        
        p = connect_cvs_btn.palette()
        p.setColor(connect_cvs_btn.backgroundRole(), QtGui.QColor(0,100,0))
        connect_cvs_btn.setPalette(p)

        # break connections        
        break_con_btn = QtGui.QPushButton('Break connection')
        vbox.addWidget(break_con_btn)
        break_con_btn.clicked.connect(self.break_con_btn_clicked)
        
        p = break_con_btn.palette()
        p.setColor(break_con_btn.backgroundRole(), QtGui.QColor(100,0,0))
        break_con_btn.setPalette(p)
           
        
        vbox.addStretch()
        
    def create_canvas_node_btn_clicked(self):
        
        canvasNode = pm.createNode('canvasNode')
        path = '/Users/johan/Dev/fabricEngine/canvas/polygon/twoCircleTangent/twoCircleTangentXfoFlip.canvas'
        pm.dfgImportJSON(m=canvasNode, f=path)
        self.canvas_lineedit.setText(canvasNode.name())
        
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

#show()