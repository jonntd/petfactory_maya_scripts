from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import pymel.core as pm

import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

import petfactory.util.verify as pet_verify
reload(pet_verify)

import petfactory.util.transformation_util as transformation_util
reload(transformation_util)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

         
class CreateCurveWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(CreateCurveWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        
        self.resize(300,100)
        self.setWindowTitle("Create curve")
        
        # layout
        main_layout = QtGui.QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout)
        
        '''
        self.menu_bar = QtGui.QMenuBar()
        main_layout.addWidget(self.menu_bar)
        file_menu = self.menu_bar.addMenu('File')
        
        self.send_u_param_data_action = QtGui.QAction('Send u param data', self)
        self.send_u_param_data_action.triggered.connect(self.send_u_param_data)
        file_menu.addAction(self.send_u_param_data_action)
        '''

        
        # layout
        content_layout = QtGui.QVBoxLayout()
        content_layout.setContentsMargins(7,7,7,7)
        main_layout.addLayout(content_layout)
          
        self.number_of_cvs_spinbox = simple_widget.add_spinbox(label='Number of CVs', parent_layout=content_layout, min=3, max=999, default=10)
   
        
        create_curve_button = QtGui.QPushButton('Create curve')
        create_curve_button.clicked.connect(self.create_curve_button_clicked)
        
        content_layout.addStretch()
        
        content_layout.addWidget(create_curve_button)
                
        
    def create_curve_button_clicked(self):
                
        if not pet_verify.verify_selection(pm.nodetypes.NurbsCurve):
            pm.warning('Select a NurbsCurve!')
            return
            
        crv = pet_verify.to_transform(pm.ls(sl=True)[0])
        
        num_pos = self.number_of_cvs_spinbox.value()
        u_param_list = None
        start_offset = 0
        end_offset = 0
        show_cvs = True
        new_crv = transformation_util.create_curve_from_curve(crv, num_pos, start_offset, end_offset, u_param_list, show_cvs)
        
        #tm = pm.datatypes.TransformationMatrix(crv.getMatrix()).asRotateMatrix()
        new_crv.setMatrix(crv.getMatrix())
        
                                            
def show():
    win = CreateCurveWidget(parent=maya_main_window())
    win.show()
    return win

'''
try:
    win.close()
    
except NameError:
    pass
    
win = show()
win.move(100,150)
'''