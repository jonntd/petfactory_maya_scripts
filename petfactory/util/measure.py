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
    
# popup win

class PopupDialog(QtGui.QDialog):
    
    def __init__(self, parent=None):
        
        super(PopupDialog, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.Tool)
        self.resize(150, 150)
        self.setWindowTitle("Set Drawing Overide")
        self.color_index = 0
        
        # layout
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)
        vertical_layout.setContentsMargins(2,2,2,2)
        
        # use shape
        grid_horiz_layout = QtGui.QHBoxLayout()
        vertical_layout.addLayout(grid_horiz_layout)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(1)
        grid.setContentsMargins(0,0,0,0)


        num_buttons = 32
        btn_per_row = 8

        for n in range(0, num_buttons):
            
            if n is 0:
                color_float = (.471, .471, .471)
                
            else:
                color_float = pm.colorIndex(n, q=True)

            color = QtGui.QColor()

            color.setRgbF(color_float[0], color_float[1], color_float[2])
            pixmap = QtGui.QPixmap(50, 50)
            pixmap.fill(QtGui.QColor(color))
            icon = QtGui.QIcon(pixmap)
            
            button = QtGui.QPushButton(icon, "")
            
            button.setMinimumSize(50,50)
            button.setMaximumSize(50,50)
            button.setIconSize(QtCore.QSize(50,50))
            button.color_index = n
            button.clicked.connect(self.selectColor)
            grid.addWidget(button, (n)/btn_per_row, (n)%btn_per_row)
            

        grid_horiz_layout.addLayout(grid)
        grid_horiz_layout.addStretch()
        
        # OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        vertical_layout.addWidget(buttons)
        
        vertical_layout.addStretch()

        self.show()
        
    def selectColor(self):
        self.color_index = self.sender().color_index
        
    def dialogButtonClicked(self, btn):
        print(btn)
        
    @staticmethod
    def getPopupInfo(parent = None):
        
        dialog = PopupDialog(parent)
        result = dialog.exec_()     
        return (dialog.color_index, result == QtGui.QDialog.Accepted)
        
          
class MeasureWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(MeasureWidget, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 250, 100)
        self.setWindowTitle('Measure')
        self.color_index = 0
        
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
        
        loc_size_label = QtGui.QLabel('Loc size')
        loc_size_label.setMaximumWidth(50)
        loc_size_hbox.addWidget(loc_size_label)        
        
        self.loc_size_spinbox = QtGui.QDoubleSpinBox()
        self.loc_size_spinbox.setValue(1.0)
        self.loc_size_spinbox.setSingleStep(0.1)
        loc_size_hbox.addWidget(self.loc_size_spinbox)
        
        
        # select color
        
        self.select_color_button = QtGui.QPushButton('Color')
        loc_size_hbox.addWidget(self.select_color_button)
        self.select_color_button.clicked.connect(self.select_color_clicked)
        self.update_current_color()
        
        vbox.addStretch()
    
    def update_current_color(self):
        
        if self.color_index is 0:
            color_float = (.471, .471, .471)
                
        else:
            color_float = pm.colorIndex(self.color_index, q=True)
                
        color = QtGui.QColor()

        color.setRgbF(color_float[0], color_float[1], color_float[2])
        pixmap = QtGui.QPixmap(50, 50)
        pixmap.fill(QtGui.QColor(color))
        icon = QtGui.QIcon(pixmap)
        
        self.select_color_button.setIcon(icon)
        print(icon)
            
    def select_color_clicked(self):
        
        (self.color_index, result) = PopupDialog.getPopupInfo(self)
        
        if result:
            print(self.color_index)
            self.update_current_color()
            
        else:
            #print('canceled!')
            pass
        
    def measure_locked_axis(self, axis):
        createMeasureGrpFromSel(lockAxis=True, loc_size=self.loc_size_spinbox.value(), freeAxis=axis, useComponents=self.use_verts_checkbox.isChecked(), color_index=self.color_index)
        
    def measure_free_axis(self):
        createMeasureGrpFromSel(lockAxis=False, loc_size=self.loc_size_spinbox.value(), useComponents=self.use_verts_checkbox.isChecked(), color_index=self.color_index)
        
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