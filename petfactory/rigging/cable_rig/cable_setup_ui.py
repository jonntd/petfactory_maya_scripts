from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
from functools import partial
import pprint

import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

import petfactory.util.verify as pet_verify
reload(pet_verify)

import petfactory.rigging.cable_rig.cable_setup as cable_setup
reload(cable_setup)

import petfactory.rigging.joints.create_curve_joints_ui as create_curve_joints_ui
reload(create_curve_joints_ui)

import petfactory.util.attr as pet_attr
reload(pet_attr)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
class MySpinboxDelegate(QtGui.QItemDelegate):
    
    def __init__(self, parent=None):
        super(MySpinboxDelegate, self).__init__(parent)
        
    def createEditor(self, parent, option, index):
        
        row = index.row()
        
        spinbox = QtGui.QDoubleSpinBox(parent)
        spinbox.setDecimals(4)
        spinbox.setRange(0, 1.0)
        spinbox.setSingleStep(.01)
        spinbox.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        
        return spinbox

class CableSetupWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(CableSetupWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,100)
        self.setWindowTitle("Cable Setup")

        
        self.preview_joint_spacing_ui = None
        
        
        # layout
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)
        vertical_layout.setContentsMargins(0,0,0,0)

        
        tab_widget = QtGui.QTabWidget()
        vertical_layout.addWidget(tab_widget)
        

        
        # tab widgts and layout
        # tab 1        
        tab_1 = QtGui.QWidget()
        tab_widget.addTab(tab_1, "Setup")  
        tab_1_vertical_layout = QtGui.QVBoxLayout(tab_1)
        
        # tab 2 
        tab_2 = QtGui.QWidget()
        tab_widget.addTab(tab_2, "Sets")  
        tab_2_vertical_layout = QtGui.QVBoxLayout(tab_2)
        
        # tab 2 
        tab_3 = QtGui.QWidget()
        tab_widget.addTab(tab_3, "Joints")  
        tab_3_vertical_layout = QtGui.QVBoxLayout(tab_3)

          
        # tree view
        self.model = QtGui.QStandardItemModel()
        
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree_view.setAlternatingRowColors(True)
 

        self.tree_view.setModel(self.model)
        tab_1_vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['Cable curves', 'Name'])
                
        # add joint ref
        self.joint_ref_horiz_layout = QtGui.QHBoxLayout()
        tab_1_vertical_layout.addLayout(self.joint_ref_horiz_layout)        
        
        # add
        self.add_joint_ref_button = QtGui.QPushButton(' + ')
        self.add_joint_ref_button.setMinimumWidth(40)
        
        self.joint_ref_horiz_layout.addWidget(self.add_joint_ref_button)
        self.add_joint_ref_button.clicked.connect(self.add_joint_ref_click)
        
        # remove
        self.remove_joint_ref_button = QtGui.QPushButton(' - ')
        self.remove_joint_ref_button.setMinimumWidth(40)
        
        self.joint_ref_horiz_layout.addWidget(self.remove_joint_ref_button)
        self.remove_joint_ref_button.clicked.connect(self.remove_joint_ref_click)
        
        self.joint_ref_label = QtGui.QLabel('Add / Remove curves')
        self.joint_ref_horiz_layout.addWidget(self.joint_ref_label)
        self.joint_ref_horiz_layout.addStretch()
        
        
        # rig group box
        rig_group_box = QtGui.QGroupBox("Rig Properties")
        tab_1_vertical_layout.addWidget(rig_group_box)
        rig_group_vert_layout = QtGui.QVBoxLayout()
        rig_group_box.setLayout(rig_group_vert_layout)
        
        
        
        # rig name
        self.name_horiz_layout = QtGui.QHBoxLayout()
        rig_group_vert_layout.addLayout(self.name_horiz_layout)
        
        self.name_label = QtGui.QLabel('Rig name')
        self.name_horiz_layout.addWidget(self.name_label)
        
        self.name_line_edit = QtGui.QLineEdit()
        self.name_horiz_layout.addWidget(self.name_line_edit)
        
        
        # add_spinbox(label, parent_layout, min=None, max=None, default=None, double_spinbox=False):
        self.name_start_index_spinbox = simple_widget.add_spinbox(label='Name start index', parent_layout=rig_group_vert_layout, min=0, max=999)
        self.cable_radius_spinbox = simple_widget.add_spinbox(label='Cable radius', parent_layout=rig_group_vert_layout, min=.1, max=999, default=1, double_spinbox=True)
        self.cable_axis_divisions_spinbox = simple_widget.add_spinbox(label='Cable axis divisions', parent_layout=rig_group_vert_layout, min=3, max=99, default=12)
        self.cable_ik_joints_spinbox = simple_widget.add_spinbox(label='Cable IK joints', parent_layout=rig_group_vert_layout, min=3, max=10, default=4)
        self.cable_ik_joints_spinbox.valueChanged.connect(self.number_of_joints_changed)
        
        self.cable_bind_joints_spinbox = simple_widget.add_spinbox(label='Cable bind joints', parent_layout=rig_group_vert_layout, min=3, max=99, default=10)

        
        # hairsystem group box
        hairsystem_group_box = QtGui.QGroupBox("Hairsystem")
        tab_1_vertical_layout.addWidget(hairsystem_group_box)
        hairsystem_group_vert_layout = QtGui.QVBoxLayout()
        hairsystem_group_box.setLayout(hairsystem_group_vert_layout)
        
        # use existing hairsystem group box
        self.use_existing_group_box = QtGui.QGroupBox("Use existing")
        hairsystem_group_vert_layout.addWidget(self.use_existing_group_box)
        self.use_existing_group_box.setCheckable(True)
        self.use_existing_group_box.setChecked(False)
        
        use_existing_group_box_vert_layout = QtGui.QVBoxLayout()
        self.use_existing_group_box.setLayout(use_existing_group_box_vert_layout)
        self.use_existing_group_box.clicked.connect(self.hairsystem_groupbox_clicked)


        self.existing_hairsystem_line_edit = simple_widget.add_populate_lineedit(label='Hairsystem >', parent_layout=use_existing_group_box_vert_layout, callback=self.populate_lineedit, kwargs={'type':pm.nodetypes.HairSystem, 'use_shape':True})

        
        # share hairsystem
        # create new hairsystem group box
        self.create_new_group_box = QtGui.QGroupBox("Create new")
        self.create_new_group_box.clicked.connect(self.hairsystem_groupbox_clicked)
        hairsystem_group_vert_layout.addWidget(self.create_new_group_box)
        self.create_new_group_box.setCheckable(True)
        create_new_group_box_vert_layout = QtGui.QVBoxLayout()
        self.create_new_group_box.setLayout(create_new_group_box_vert_layout)
        
        
        
        
        self.share_hairsystem_widget = QtGui.QWidget()

        create_new_group_box_vert_layout.addWidget(self.share_hairsystem_widget)

        
        share_hairsystem_horiz_layout = QtGui.QHBoxLayout()
        self.share_hairsystem_widget.setLayout(share_hairsystem_horiz_layout)

        self.share_hairsystem_checkbox = QtGui.QCheckBox()
        share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_checkbox)
        
        self.share_hairsystem_label = QtGui.QLabel('Share Hairsystem')
        share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_label)
        share_hairsystem_horiz_layout.addStretch()
        
 

        # Setup
        self.setup_horiz_layout = QtGui.QHBoxLayout()
        tab_1_vertical_layout.addLayout(self.setup_horiz_layout)
        
        self.setup_button = QtGui.QPushButton('Setup Cables')
        self.setup_button.setMinimumWidth(125)
        self.setup_horiz_layout.addStretch()
        self.setup_horiz_layout.addWidget(self.setup_button)
        self.setup_button.clicked.connect(self.setup_cable)
        
        
        
        
        # Sets (tab 2)
        
        # rig group box
        self.sets_group_box = QtGui.QGroupBox("Use existing Sets")
        self.sets_group_box.setCheckable(True)
        self.sets_group_box.setChecked(False)
        tab_2_vertical_layout.addWidget(self.sets_group_box)
        sets_group_vert_layout = QtGui.QVBoxLayout()
        self.sets_group_box.setLayout(sets_group_vert_layout)
        
  
        self.mesh_set_lineedit = simple_widget.add_populate_lineedit(label='Mesh       >', parent_layout=sets_group_vert_layout, callback=self.populate_lineedit, kwargs={'type':pm.nodetypes.ObjectSet})
        self.start_ctrl_set_lineedit = simple_widget.add_populate_lineedit(label='Start ctrl >', parent_layout=sets_group_vert_layout, callback=self.populate_lineedit, kwargs={'type':pm.nodetypes.ObjectSet})
        self.end_ctrl_set_lineedit = simple_widget.add_populate_lineedit(label='End ctrl   >', parent_layout=sets_group_vert_layout, callback=self.populate_lineedit, kwargs={'type':pm.nodetypes.ObjectSet})
        self.follicle_set_lineedit = simple_widget.add_populate_lineedit(label='Follicle   >', parent_layout=sets_group_vert_layout, callback=self.populate_lineedit, kwargs={'type':pm.nodetypes.ObjectSet})
        
        tab_2_vertical_layout.addStretch()
        
        # Joints (tab 3)        
        
        # custom joint spacing group box
        self.custom_joint_spacing_groupbox = QtGui.QGroupBox("Custom joint spacing")
        self.custom_joint_spacing_groupbox.setCheckable(True)
        self.custom_joint_spacing_groupbox.setChecked(False)
        tab_3_vertical_layout.addWidget(self.custom_joint_spacing_groupbox)
        custom_joint_spacing_groupbox_vbox = QtGui.QVBoxLayout()
        self.custom_joint_spacing_groupbox.setLayout(custom_joint_spacing_groupbox_vbox)

        # model
        self.joint_spacing_model = QtGui.QStandardItemModel()
        self.joint_spacing_model.setHorizontalHeaderLabels(['joint u parameter'])
       
        # tableview 
        self.joint_spacing_tableview = QtGui.QTableView()
        custom_joint_spacing_groupbox_vbox.addWidget(self.joint_spacing_tableview)
        self.joint_spacing_tableview.setAlternatingRowColors(True)
        self.joint_spacing_tableview.setModel(self.joint_spacing_model)   
        h_header = self.joint_spacing_tableview.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Stretch)
        self.joint_spacing_tableview.setItemDelegate(MySpinboxDelegate(self.joint_spacing_tableview))
        
        self.update_data_model(self.cable_ik_joints_spinbox.value())
        
        
        # preview joints
        
        get_spacing_from_curve_button = QtGui.QPushButton('Get setup info from curve')
        get_spacing_from_curve_button.clicked.connect(self.get_spacing_from_curve_button_clicked)
        tab_3_vertical_layout.addWidget(get_spacing_from_curve_button)
        
        
        preview_joints_button = QtGui.QPushButton('Open create curve joints ui')
        preview_joints_button.clicked.connect(self.preview_joints_button_clicked)
        tab_3_vertical_layout.addWidget(preview_joints_button)
        
        
        export_import_hbox = QtGui.QHBoxLayout()
        tab_3_vertical_layout.addLayout(export_import_hbox)
        refresh_joint_spacing_button = QtGui.QPushButton('>> Import')
        refresh_joint_spacing_button.clicked.connect(partial(self.transfer_joint_spacing_button_clicked, direction='export'))
        export_import_hbox.addWidget(refresh_joint_spacing_button)
        
        refresh_joint_spacing_button = QtGui.QPushButton('Export >>')
        refresh_joint_spacing_button.clicked.connect(partial(self.transfer_joint_spacing_button_clicked, direction='import'))
        export_import_hbox.addWidget(refresh_joint_spacing_button)
                
        #tab_2_vertical_layout.addStretch()
    
    def update_data_model(self, num_ik_joints):
        
        # clear the model
        self.joint_spacing_model.removeRows(0, self.joint_spacing_model.rowCount())
        
        num_bones = num_ik_joints-1
        if num_bones == 0:
            num_bones = 1
            
        inc = 1.0 / num_bones
        
        for row in range(num_ik_joints):
            
            if num_ik_joints > 1:
                    val = '{:.4f}'.format(inc*row)
            else:
                val = '{:.4f}'.format(.5)
                    
            item = QtGui.QStandardItem(val)
            
            self.joint_spacing_model.setItem(row, 0, item)

    def get_spacing_from_curve_button_clicked(self):
        
        if pet_verify.verify_selection(pm.nodetypes.NurbsCurve):
            
            json_dict = pet_attr.get_json_attr(pm.ls(sl=True)[0])
            
            # found a dict
            if json_dict is not None:

                cable_axis_divisions = json_dict.get('cable_axis_divisions')
                cable_radius = json_dict.get('cable_radius')
                joint_spacing_list = json_dict.get('joint_spacing_list')
                name_start_index = json_dict.get('name_start_index')
                num_bind_joints = json_dict.get('num_bind_joints')
                num_ik_joints = json_dict.get('num_ik_joints')
                
                if cable_axis_divisions is not None:
                    self.cable_axis_divisions_spinbox.setValue(cable_axis_divisions)
                
                if cable_radius is not None:
                    self.cable_radius_spinbox.setValue(cable_radius)
                    
                if name_start_index is not None:
                    self.name_start_index_spinbox.setValue(name_start_index)
                    
                if num_bind_joints is not None:
                    self.cable_bind_joints_spinbox.setValue(num_bind_joints)
                
                if num_ik_joints is not None:
                    self.cable_ik_joints_spinbox.setValue(num_ik_joints)
                                    
            else:
                pm.warning('No json attr on curve!')
                            
        else:
            pm.warning('Select a curve!')
        
    def number_of_joints_changed(self):        
        self.update_data_model(self.sender().value())
                
           
    def transfer_joint_spacing_button_clicked(self, direction):
        
        if self.preview_joint_spacing_ui is None:
            pm.warning('Please open the Preview joints ui')
            
        else:
            num_preview_joints = self.preview_joint_spacing_ui.number_of_joints_spinbox.value()
            num_ik_joints = self.cable_ik_joints_spinbox.value()
            
            if num_preview_joints != num_ik_joints:
                pm.warning('Number of joints do not match, pleas use {0} preview joints'.format(num_ik_joints))
                return
            
            
            if direction == 'export':
                # get the data
                num_rows = self.preview_joint_spacing_ui.model.rowCount()
                
                for row in range(num_rows):
                    val = self.preview_joint_spacing_ui.model.item(row, 0).text()
                    self.joint_spacing_model.item(row, 0).setText(val)
            else:
                print('import')
            
                            
    
    def preview_joints_button_clicked(self):
        
        if self.preview_joint_spacing_ui is None:
            self.preview_joint_spacing_ui = create_curve_joints_ui.show()
            
        else:
            self.preview_joint_spacing_ui.show()
        
    def populate_lineedit(self, **kwargs):
        
        lineedit = kwargs.get('lineedit')

        sel = pm.ls(sl=True)
        
        if not sel:
            pm.warning('Nothing is selected!')
            return
            
        else: 
        
            type = kwargs.get('type')
            
            if type:
                if pet_verify.verify_string(sel[0], type):
                    lineedit.setText(sel[0].longName())
                else:
                    pm.warning('Make sure the selected node is of type: {0}'.format(type))
        

    def add_joint_ref_click(self):
        

        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a curve!')
            return
        
        for sel in sel_list:
            
            if not pet_verify.verify_pynode(sel, pm.nodetypes.NurbsCurve):
                pm.warning('{0} is not a curve, skipped'.format(sel.name()))
                continue
            
            # if we have selected a crv, get the parent transform
            if isinstance(sel, pm.nodetypes.NurbsCurve):
                sel = sel.getParent()
                
            item = QtGui.QStandardItem(sel.name())
            
            # set flags
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            self.model.appendRow(item) 
                
    
    def remove_joint_ref_click(self):
        
        selection_model = self.tree_view.selectionModel()
        
        # returns QModelIndex
        selected_rows = selection_model.selectedRows()
        
        row_list = [sel.row() for sel in selected_rows]
        row_list.sort(reverse=True)
        
        for row in row_list:
            self.model.removeRow(row)
            
            
    def hairsystem_groupbox_clicked(self):
        
        is_checked = self.sender().isChecked()
        
        if self.sender() is self.use_existing_group_box:
            self.create_new_group_box.setChecked(not is_checked)
        
        else:
            self.use_existing_group_box.setChecked(not is_checked)

    
       
    def setup_cable(self):

        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
                
        # the ref grp
        if num_children < 1:
            pm.warning('No joint ref are available in the treeview!')
            return
    
        crv_list = []
        for i in range(num_children):
            
            child = root.child(i)
            
            if child.checkState():
                
                crv = pet_verify.to_pynode(child.text())
                
                if crv is not None:
                    crv_list.append(crv)
                

        rig_name = self.name_line_edit.text()
        name_start_index = self.name_start_index_spinbox.value()
        cable_radius = self.cable_radius_spinbox.value()
        cable_axis_divisions = self.cable_axis_divisions_spinbox.value()
        num_ik_joints = self.cable_ik_joints_spinbox.value()
        num_bind_joints = self.cable_bind_joints_spinbox.value()           
        use_existing_hairsystem = self.use_existing_group_box.isChecked()
        share_hairsystem = self.share_hairsystem_checkbox.isChecked()
        existing_hairsystem_unicode = self.existing_hairsystem_line_edit.text()
        mesh_set_unicode = self.mesh_set_lineedit.text()
        start_ctrl_set_unicode = self.start_ctrl_set_lineedit.text()
        end_ctrl_set_unicode = self.end_ctrl_set_lineedit.text()
        follicle_set_unicode = self.follicle_set_lineedit.text()
        use_existing_sets = self.sets_group_box.isChecked()
        
        
        if self.custom_joint_spacing_groupbox.isChecked():
               
            num_joint_spacing_rows = self.joint_spacing_model.rowCount()    
            joint_u_list = []
            for row in range(num_joint_spacing_rows):
                joint_u_list.append(float(self.joint_spacing_model.item(row, 0).text()))
                
        else:
            joint_u_list = None

        
        if rig_name == '':
            rig_name = 'cable_rig'

            
        if use_existing_hairsystem:
            existing_hairsystem = pet_verify.to_pynode(existing_hairsystem_unicode)
            if existing_hairsystem is None:
                pm.warning('Please use a valid hairsystem')
                return
                
        else:
            existing_hairsystem = None
        
        if use_existing_sets:
            mesh_set = pet_verify.to_pynode(mesh_set_unicode)
            start_ctrl_set = pet_verify.to_pynode(start_ctrl_set_unicode)
            end_ctrl_set = pet_verify.to_pynode(end_ctrl_set_unicode)
            follicle_set = pet_verify.to_pynode(follicle_set_unicode)
            
        else:
            mesh_set = start_ctrl_set = end_ctrl_set = follicle_set = None
            
        
        
       
        kwargs = {  'crv_list':crv_list,
                    'rig_name':rig_name,
                    'name_start_index':name_start_index,
                    'num_ik_joints':num_ik_joints,
                    'num_bind_joints':num_bind_joints,
                    'cable_radius':cable_radius,
                    'cable_axis_divisions':cable_axis_divisions,
                    'mesh_set':mesh_set,
                    'start_ctrl_set':start_ctrl_set,
                    'end_ctrl_set':end_ctrl_set,
                    'follicle_set':follicle_set,
                    'use_existing_hairsystem':use_existing_hairsystem,
                    'share_hairsystem':share_hairsystem,
                    'existing_hairsystem':existing_hairsystem,
                    'joint_u_list':joint_u_list
                    }
        
        #pprint.pprint(kwargs)
        cable_setup.setup_crv_list(**kwargs)


def show():      
    win = CableSetupWidget(parent=maya_main_window())
    win.show()
    return win



try:
    win.close()
    
except NameError:
    pass

win = show()
win.move(100,150)

#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_10_cvs_tripple.mb', f=True)

#pm.select(pm.PyNode('curve1'), pm.PyNode('curve2'), pm.PyNode('curve3'))
#win.add_joint_ref_click()

#pm.select(pm.PyNode('hairSystem1'))
#win.add_hairsystem_clicked()