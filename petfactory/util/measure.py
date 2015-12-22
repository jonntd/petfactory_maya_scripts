from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial


def createMeasureGrp(startPos, endPos, loc_size=1.0):
    
    locOrigo = pm.createNode('locator')
    locEnd = pm.createNode('locator')
    
    locOrigo.localScale.set(loc_size,loc_size,loc_size)
    locEnd.localScale.set(loc_size,loc_size,loc_size)
    
    locOrigoTrans = locOrigo.getParent()
    locEndTrans = locEnd.getParent()
    
    locOrigoTrans.translate.set(startPos)
    locEndTrans.translate.set(endPos)
    
    pm.parent(locEndTrans, locOrigoTrans)
            
    pm.select([locOrigo, locEnd])
    distDim = pm.distanceDimension()
    
    grp = pm.group(em=True)
    grp.rename('measureGrp')
    pm.parent(locOrigoTrans, distDim.getParent(), grp)
    

def createMeasureGrpFromSel(lockAxis, loc_size=1.0, freeAxis=0, useComponents=False):
    
    if useComponents:
        
        sel = pm.ls(orderedSelection=True)
        
    else:
        sel = pm.ls(sl=True)

    print(sel)
    
    if len(sel) < 2:
        pm.warning('Select atl east 2 nodes!')
        return            
            
    startPos = pm.xform(sel[0], query=True, translation=True, worldSpace=True)
    endPos = pm.xform(sel[1], query=True, translation=True, worldSpace=True)
        
    if lockAxis:
        
        if freeAxis == 0:
            endPos = pm.datatypes.Vector(endPos[0], startPos[1], startPos[2])
            
        elif freeAxis == 1:
            endPos = pm.datatypes.Vector(startPos[0], endPos[1], startPos[2])
            
        else:
            endPos = pm.datatypes.Vector(startPos[0], startPos[1], endPos[2])
            
        createMeasureGrp(startPos, endPos, loc_size=loc_size)
        
    else:        
        createMeasureGrp(startPos, endPos, loc_size=loc_size)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
       
class MeasureWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(MeasureWidget, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 250, 100)
        self.setWindowTitle('Measure')
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        locked_axis_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(locked_axis_hbox)
        
        # x
        measure_axis_x_btn = QtGui.QPushButton('X')
        locked_axis_hbox.addWidget(measure_axis_x_btn)
        measure_axis_x_btn.clicked.connect(partial(self.measure_locked_axis, 0))
        p = measure_axis_x_btn.palette()
        p.setColor(measure_axis_x_btn.backgroundRole(), QtGui.QColor(100, 0,0))
        measure_axis_x_btn.setPalette(p)
        
        
        
        # y
        measure_axis_y_btn = QtGui.QPushButton('Y')
        locked_axis_hbox.addWidget(measure_axis_y_btn)
        measure_axis_y_btn.clicked.connect(partial(self.measure_locked_axis, 1))
        p = measure_axis_y_btn.palette()
        p.setColor(measure_axis_y_btn.backgroundRole(), QtGui.QColor(0,100,0))
        measure_axis_y_btn.setPalette(p)
        
        
        # z
        measure_axis_z_btn = QtGui.QPushButton('Z')
        locked_axis_hbox.addWidget(measure_axis_z_btn)
        measure_axis_z_btn.clicked.connect(partial(self.measure_locked_axis, 2))
        p = measure_axis_z_btn.palette()
        p.setColor(measure_axis_z_btn.backgroundRole(), QtGui.QColor(0,0,100))
        measure_axis_z_btn.setPalette(p)
        
        # all axis
        measure_all_axis_btn = QtGui.QPushButton('All axis')
        vbox.addWidget(measure_all_axis_btn)
        measure_all_axis_btn.clicked.connect(self.measure_free_axis)
        
        # use vertices
        
        use_verts_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(use_verts_hbox)
        
        self.use_verts_checkbox = QtGui.QCheckBox('Use Vertices')
        use_verts_hbox.addWidget(self.use_verts_checkbox)
        self.use_verts_checkbox.clicked.connect(self.use_verts_cb_clicked)
        
        # locator size
        
        loc_size_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(loc_size_hbox)
        
        self.loc_size_spinbox = QtGui.QDoubleSpinBox()
        loc_size_hbox.addWidget(self.loc_size_spinbox)

        
        

        vbox.addStretch()
        
    def measure_locked_axis(self, axis):
        createMeasureGrpFromSel(lockAxis=True, loc_size=self.loc_size_spinbox.value(), freeAxis=axis, useComponents=self.use_verts_checkbox.isChecked())
        
    def measure_free_axis(self):
        createMeasureGrpFromSel(lockAxis=False, loc_size=self.loc_size_spinbox.value(), useComponents=self.use_verts_checkbox.isChecked())
        
    def use_verts_cb_clicked(self):
        
        #pm.selectPref(trackSelectionOrder=True, q=True)
        
        # we need to tell maya that we are intersested in theselection order of components
        if self.sender().isChecked():
            pm.selectPref(trackSelectionOrder=True)
        else:
            pm.selectPref(trackSelectionOrder=False)
            
             
def show():
    win = MeasureWidget(parent=maya_main_window())
    win.show()

#show()