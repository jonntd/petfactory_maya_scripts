from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm

import petfactory.gui.simple_widget as simple_widget

import trans_to_volume_ray

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
  
class TransToVolumeRay(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(TransToVolumeRay, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(200,100)
        self.setWindowTitle("Trans to Volume Ray")
        
        main_vbox = QtGui.QVBoxLayout()
        self.setLayout(main_vbox)
        
        self.x_min = simple_widget.add_spinbox(label='x min', parent_layout=main_vbox, min=-999, max=999, default=-1, double_spinbox=True, decimals=3)
        self.x_max = simple_widget.add_spinbox(label='x max', parent_layout=main_vbox, min=-999, max=999, default=1, double_spinbox=True, decimals=3)
        self.y_min = simple_widget.add_spinbox(label='y min', parent_layout=main_vbox, min=-999, max=999, default=-1, double_spinbox=True, decimals=3)
        self.y_max = simple_widget.add_spinbox(label='y max', parent_layout=main_vbox, min=-999, max=999, default=1, double_spinbox=True, decimals=3)
        self.bb_multiplier = simple_widget.add_spinbox(label='BB Multiplier', parent_layout=main_vbox, min=-999, max=999, default=1, double_spinbox=True, decimals=3)
        self.z_offset = simple_widget.add_spinbox(label='z offset', parent_layout=main_vbox, min=-999, max=999, default=-3, double_spinbox=True, decimals=3)
                
        main_vbox.addStretch()
        
        copy_button = QtGui.QPushButton('Copy to Nuke')
        main_vbox.addWidget(copy_button)
        
        copy_button.clicked.connect(self.copy_button_clicked)

    
    def copy_button_clicked(self):
        
        sel_list = pm.ls(sl=True)
        if len(sel_list) < 1:
            pm.warning('Nothong is selected!')
            return

        frame_start = int(pm.playbackOptions(q=True, min=True))
        frame_end = int(pm.playbackOptions(q=True, max=True))
        x_min = self.x_min.value()
        x_max = self.x_max.value()
        y_min = self.y_min.value()
        y_max = self.y_max.value()
        mult = self.bb_multiplier.value()

        pos_list = [    pm.datatypes.VectorN(x_max*mult, y_max*mult, 0, 1),
                        pm.datatypes.VectorN(x_min*mult ,y_max*mult, 0, 1),
                        pm.datatypes.VectorN(x_min*mult ,y_min*mult, 0, 1),
                        pm.datatypes.VectorN(x_max*mult ,y_min*mult, 0, 1)]

        z_offset = self.z_offset.value()

        trans_to_volume_ray.build_nuke_voulume_ray( sel_list,
                                                    pos_list,
                                                    z_offset,
                                                    frame_start,
                                                    frame_end)

def show():
    win = TransToVolumeRay(parent=maya_main_window())
    win.show()

'''
try:
    win.close()
    
except NameError:
    print('No win to close')
    
win = RegexWidget(parent=maya_main_window())
win.show()
win.move(100,250)
'''
