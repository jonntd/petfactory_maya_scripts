from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial


def createMeasureGrp(startPos, endPos, loc_size=1.0, color_index=12):
    
    grp = pm.group(em=True)
    grp.rename('measureGrp')
    grp.translate.set(startPos)
    
    locOrigo = pm.createNode('locator')
    locEnd = pm.createNode('locator')
    
    locOrigo.localScale.set(loc_size,loc_size,loc_size)
    locEnd.localScale.set(loc_size,loc_size,loc_size)
    
    locOrigoTrans = locOrigo.getParent()
    locEndTrans = locEnd.getParent()
    
    locOrigoTrans.translate.set(startPos)
    locEndTrans.translate.set(endPos)
            
    pm.select([locOrigo, locEnd])
    distDim = pm.distanceDimension()
    
    pm.parent(locEndTrans, locOrigoTrans, distDim.getParent(), grp)
    
    locOrigo.overrideEnabled.set(True)
    locEnd.overrideEnabled.set(True)
    distDim.overrideEnabled.set(True)
    
    locOrigo.overrideColor.set(color_index)
    locEnd.overrideColor.set(color_index)
    distDim.overrideColor.set(color_index)
    

def createMeasureGrpFromSel(lockAxis, loc_size=1.0, freeAxis=0, useComponents=False, color_index=None):
    
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
            
        createMeasureGrp(startPos, endPos, loc_size=loc_size, color_index=color_index)
        
    else:        
        createMeasureGrp(startPos, endPos, loc_size=loc_size, color_index=color_index)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
              
class MeasureWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(MeasureWidget, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 180, 100)
        self.setWindowTitle('Measure')
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        locked_axis_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(locked_axis_hbox)
        
        # x
        measure_axis_x_btn = QtGui.QPushButton('X')
        locked_axis_hbox.addWidget(measure_axis_x_btn)
        measure_axis_x_btn.clicked.connect(partial(self.measure_locked_axis, 0))
        measure_axis_x_btn.setStyleSheet('QPushButton { color: #dd0000; font-style: bold  }')
                
        # y
        measure_axis_y_btn = QtGui.QPushButton('Y')
        locked_axis_hbox.addWidget(measure_axis_y_btn)
        measure_axis_y_btn.clicked.connect(partial(self.measure_locked_axis, 1))
        measure_axis_y_btn.setStyleSheet('QPushButton { color: #00aa00; font-style: bold  }')        
        
        # z
        measure_axis_z_btn = QtGui.QPushButton('Z')
        locked_axis_hbox.addWidget(measure_axis_z_btn)
        measure_axis_z_btn.clicked.connect(partial(self.measure_locked_axis, 2))
        measure_axis_z_btn.setStyleSheet('QPushButton { color: #0000dd; font-style: bold  }')
        
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
        
        loc_size_label = QtGui.QLabel('Loc size')
        loc_size_label.setMaximumWidth(50)
        loc_size_hbox.addWidget(loc_size_label)        
        
        self.loc_size_spinbox = QtGui.QDoubleSpinBox()
        self.loc_size_spinbox.setValue(1.0)
        self.loc_size_spinbox.setSingleStep(0.1)
        loc_size_hbox.addWidget(self.loc_size_spinbox)
        
        
        # select color
        
        self.select_color_button = QtGui.QPushButton('Color')
        self.select_color_button.setFixedWidth(90)
        loc_size_hbox.addWidget(self.select_color_button)
        
        
        self.menu = QtGui.QMenu(self)
        self.select_color_button.setMenu(self.menu)
        
        self.num_colors = 32
        self.current_color_index = 0
                
        for i in range(self.num_colors ):
            self.add_menu_items(self.menu, i)
                       
        self.set_color(self.current_color_index)

        
        vbox.addStretch()
        
    def add_menu_items(self, menu, color_index):
                    
        if color_index is 0:
            color_float = (.471, .471, .471)
                
        else:
            color_float = pm.colorIndex(color_index, q=True)

        color = QtGui.QColor()
        color.setRgbF(color_float[0], color_float[1], color_float[2])
        
        pixmap = QtGui.QPixmap(50, 50)
        pixmap.fill(QtGui.QColor(color))
        icon = QtGui.QIcon(pixmap)
        
        action = QtGui.QAction(icon, str(color_index), self)
        action.triggered.connect(partial(self.set_color, color_index))
        
        menu.addAction(action)

        
    def set_color(self, color_index):
        
        if color_index is 0:
            color_float = (.471, .471, .471)
                
        else:
            color_float = pm.colorIndex(color_index, q=True)

        color = QtGui.QColor()
        color.setRgbF(color_float[0], color_float[1], color_float[2])
        
        pixmap = QtGui.QPixmap(50, 50)
        pixmap.fill(QtGui.QColor(color))
        icon = QtGui.QIcon(pixmap)
        
        self.select_color_button.setIcon(icon)
        self.select_color_button.setIconSize(QtCore.QSize(10,10))
        self.select_color_button.setText('set color')
        
        self.current_color_index = color_index

        
    def measure_locked_axis(self, axis):
        createMeasureGrpFromSel(lockAxis=True, loc_size=self.loc_size_spinbox.value(), freeAxis=axis, useComponents=self.use_verts_checkbox.isChecked(), color_index=self.current_color_index)
        
    def measure_free_axis(self):
        createMeasureGrpFromSel(lockAxis=False, loc_size=self.loc_size_spinbox.value(), useComponents=self.use_verts_checkbox.isChecked(), color_index=self.current_color_index)
        
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