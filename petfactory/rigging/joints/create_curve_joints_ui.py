from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import re
import pymel.core as pm

import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

import petfactory.util.verify as pet_verify
reload(pet_verify)

import petfactory.rigging.joints.create_joints as create_joints
reload(create_joints)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
  
class MySpinboxDelegate(QtGui.QItemDelegate):
    
    def __init__(self, parent=None, my_widget=None):
        super(MySpinboxDelegate, self).__init__(parent)
        self.my_widget = my_widget
        
    def createEditor(self, parent, option, index):
        
        column = index.column()
        row = index.row()
        
        if column == 0: 
            spinbox = QtGui.QDoubleSpinBox(parent)
            spinbox.setRange(0, 1.0)
            spinbox.setSingleStep(.01)
            spinbox.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            
            spinbox.valueChanged.connect(partial(self.my_widget.tableview_spinbox_delegate_changed, row))
            
            return spinbox
        
        else:
            return QtGui.QLineEdit(parent)
            
            
            
class CreateCurveJointsWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(CreateCurveJointsWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.active_set = None
        
        self.resize(300,100)
        self.setWindowTitle("Create curve joints")
        
        # layout
        main_layout = QtGui.QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout)
        
        
        self.menu_bar = QtGui.QMenuBar()
        main_layout.addWidget(self.menu_bar)
        file_menu = self.menu_bar.addMenu('File')
        
        self.send_u_param_data_action = QtGui.QAction('Send u param data', self)
        self.send_u_param_data_action.triggered.connect(self.send_u_param_data)
        file_menu.addAction(self.send_u_param_data_action)


        self.target_widget = None
        self.result_joints = None
        
        # layout
        content_layout = QtGui.QVBoxLayout()
        content_layout.setContentsMargins(7,7,7,7)
        main_layout.addLayout(content_layout)
        
        self.curve_lineedit = simple_widget.add_filtered_populate_lineedit(label='Add curve >', parent_layout=content_layout, nodetype=pm.nodetypes.NurbsCurve)
        self.number_of_joints_spinbox = simple_widget.add_spinbox(label='Number of joints', parent_layout=content_layout, min=1, max=999, default=4)
        self.number_of_joints_spinbox.valueChanged.connect(self.number_of_joints_changed)
        
        # add model and tableview
        self.model = QtGui.QStandardItemModel()
        self.u_param_tableview = QtGui.QTableView()
        self.u_param_tableview.setModel(self.model)
        self.u_param_tableview.setItemDelegate(MySpinboxDelegate(self.u_param_tableview, self))
        
        self.model.setHorizontalHeaderLabels(['joint u parameter'])
        
        h_header = self.u_param_tableview.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Stretch)
        
        content_layout.addWidget(self.u_param_tableview)

        #content_layout.addStretch()
        
        self.update_data_model(self.number_of_joints_spinbox.value())
        
            
        
        create_joints_button = QtGui.QPushButton('Create joints')
        create_joints_button.clicked.connect(self.create_joints_button_clicked)
        content_layout.addWidget(create_joints_button)
    
    def number_of_joints_changed(self):
        
        num_joints = self.sender().value()
        self.update_data_model(num_joints)
        
        self.do_create_joints()
        
    
    def tableview_spinbox_delegate_changed(self, row, val):
        
        index = self.model.index(row, 0)
        self.model.setData(index, val)
        
        self.do_create_joints()
        
        
    def update_data_model(self, num_joints):
        
        # clear the model
        self.model.removeRows(0, self.model.rowCount())
        
        num_bones = num_joints-1
        if num_bones == 0:
            num_bones = 1
            
        inc = 1.0 / num_bones
        
        for row in range(num_joints):
            
            if num_joints > 1:
                    val = str(inc*row)
            else:
                val = '0.5'
                    
            item = QtGui.QStandardItem(val)
            
            self.model.setItem(row, 0, item)
    
        
    def closeEvent(self, event):
        
        # if we want to give the user a popup to perhaps seve or something
        '''
        if some_logic_condition:
            event.accept()
        else:
            event.ignore()
        '''
        # set the reference to the target model to none
        self.target_widget = None
        
        
    def send_u_param_data(self):
        
        print(self.target_widget)
        if isinstance(self.target_widget, QtGui.QWidget):
            print('valid model', self.target_widget)
            
            print(self.target_widget.curve_lineedit.text())
            
    def set_target_model(self, target):
        
        if isinstance(target, QtGui.QWidget):
            self.target_widget = target
        else:
            pm.warning('Pleas use a QWidget as target widget')
        
    
    def do_create_joints(self):
        
        # delete joint list
        if self.result_joints is not None:
            
            try:
                pm.delete(self.result_joints)
                
            except pm.general.MayaNodeError as e:
                pm.warning(e)
                
            self.result_joints = None
            
            
        curve_unicoide = self.curve_lineedit.text()
        
        curve_node = pet_verify.to_pynode(curve_unicoide)
        num_joints = self.number_of_joints_spinbox.value()
        
        if curve_node is None:
            pm.warning('Not a valid curve')
            return
            
        num_rows = self.model.rowCount()
        
        joint_u_list = []
        for row in range(num_rows):
            joint_u_list.append(float(self.model.item(row).text()))
            
        print(curve_node, num_joints,joint_u_list)
        

        self.result_joints = create_joints.create_joints_on_curve(  crv=curve_node,
                                                                    num_joints=num_joints,
                                                                    up_axis=2,
                                                                    parent_joints=True,
                                                                    show_lra=True,
                                                                    name='joint',
                                                                    start_offset=0,
                                                                    end_offset=0,
                                                                    joint_u_list=joint_u_list)
                    
        
    def create_joints_button_clicked(self):
    
        self.do_create_joints()
        
        
        
                                            
def show():
    win = CreateCurveJointsWidget(parent=maya_main_window())
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

#win.set_target_model(show())
#win.curve_lineedit.setText('curve1')