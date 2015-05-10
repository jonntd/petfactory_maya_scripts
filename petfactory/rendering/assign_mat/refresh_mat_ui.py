from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import pymel.core as pm

import petfactory.util.verify as pet_verify

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
    
class RemapMaterialWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
 
        self.curr_mat_list = None
        self.import_mat_list = None
        self.namespace = 'lookdev'
        
        super(RemapMaterialWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(400,400)
        self.setWindowTitle("Import materials")
        
        # layout
        main_vbox = QtGui.QVBoxLayout()
        main_vbox.setContentsMargins(5,5,5,5)
        self.setLayout(main_vbox)
                
        # models
        self.mat_model = QtGui.QStandardItemModel()
        self.mat_model.setHorizontalHeaderLabels(['Current Material', 'Imported Material'])
                     
        # tableviews
        # curr mat tableview
        self.mat_tableview = QtGui.QTableView()
        self.mat_tableview.setModel(self.mat_model)
        mat_header = self.mat_tableview.horizontalHeader()
        mat_header.setStretchLastSection(True)
        main_vbox.addWidget(self.mat_tableview)
        self.mat_tableview.setColumnWidth(0, 200)
        
        self.mat_tableview.setModel(self.mat_model)
        
        self.add_current_mat_button = QtGui.QPushButton('1. List materials')
        self.add_current_mat_button.clicked.connect(self.add_mat)
        main_vbox.addWidget(self.add_current_mat_button)
        
        
        self.import_mat_button = QtGui.QPushButton('2. Import materials')
        self.import_mat_button.clicked.connect(self.import_mat)
        main_vbox.addWidget(self.import_mat_button)
        
        self.remap_mat_button = QtGui.QPushButton('3. Remap materials')
        self.remap_mat_button.clicked.connect(self.remap_mat)
        main_vbox.addWidget(self.remap_mat_button)
        
        self.remove_namespace_button = QtGui.QPushButton('4. remove namespace')
        self.remove_namespace_button.clicked.connect(self.remove_namespace)
        main_vbox.addWidget(self.remove_namespace_button)
        
        
    def list_object_from_material(self, node):
        
        # get the shading group
        sg_list = node.listConnections(type='shadingEngine')
        
        if len(sg_list) < 1:
            return (None, None)
                    
        mesh_list = []
        face_list = []
    
         
        # loop through the sg looking for members
        for sg in sg_list:
            
            member_list = sg.members(flatten=True)
            
            # loop through the members, check it the mat is assigned to faces or meshes
            for member in member_list:
    
                if type(member) == pm.nodetypes.Mesh:
                    mesh_list.append(member)
                    
                elif type(member) == pm.general.MeshFace:
                    face_list.append(member)
        
        
        return(mesh_list, face_list)
        
    def add_mat(self):
        
        self.mat_model.removeRows(0, self.mat_model.rowCount())
        
        self.curr_mat_list = [m for m in pm.ls(mat=True) if m.name() not in ['lambert1', 'particleCloud1']]
        
        for curr_mat in self.curr_mat_list:
            curr_mat_item = QtGui.QStandardItem(curr_mat.name())
            self.mat_model.appendRow(curr_mat_item)
            
            
    def import_mat(self):
        
        if self.curr_mat_list is None:
            pm.warning('Add the current materials')
            return
            
        
        file_name, selected_filter = QtGui.QFileDialog.getOpenFileName(None, 'Import Materials', None, 'Maya (*.mb *.ma)')
        
        if not file_name:
            return
            
            
            
        
        pm.importFile(file_name, namespace=self.namespace)
        
        mat_list = [m for m in pm.ls(mat=True) if m.name() not in ['lambert1', 'particleCloud1']]
        mat_set_after_import = set(mat_list)
        mat_set_before_import = set(self.curr_mat_list)            
        diff_set = mat_set_after_import.difference(mat_set_before_import)
        
        mat_dict = {}
        for node in diff_set:
            split_name = node.name().split(':')[-1]
            mat_dict[split_name] = node
            
            
        num_rows = self.mat_model.rowCount()
        

        for row in range(num_rows):
            curr_item = self.mat_model.item(row)
            new_mat = mat_dict.get(curr_item.text())
            
            if new_mat is not None:
                new_item = QtGui.QStandardItem(new_mat.name())
                self.mat_model.setItem(row, 1, new_item)
            
    
    def remap_mat(self):
        
        num_rows = self.mat_model.rowCount()
        
        for row in range(num_rows):
            
            curr_mat_item = self.mat_model.item(row)
            if curr_mat_item:
                curr_mat_node = pet_verify.to_pynode(curr_mat_item.text())
            
            new_mat_item = self.mat_model.item(row, 1)
            if new_mat_item:
                new_mat_node = pet_verify.to_pynode(new_mat_item.text())
                
            
            if curr_mat_item is None or new_mat_node is None:
                continue
                
            
            mesh_list, face_list = self.list_object_from_material(curr_mat_node)
            
            new_mat_sg_list = new_mat_node.listConnections(type='shadingEngine')
            # we get an error if we have nultiple shading groups... look into this
            
            # if we do not have a shading group create it
            if len(new_mat_sg_list) < 1:
                sg = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='{0}SG'.format(new_mat_unicode))
                new_mat_node.outColor >> sg.surfaceShader
                new_mat_sg = sg
                
            else:
                new_mat_sg = new_mat_sg_list[0]
            
            
            if mesh_list is not None:
                if len(mesh_list) > 0:
                    print(mesh_list)
                    pm.sets(new_mat_sg, forceElement=mesh_list)

        
        
    def remove_namespace(self):
        
        pm.namespace(force=True, mv=(':{0}'.format(self.namespace), ':'))

        # remove the namespace if it exists
        if pm.namespace(exists=self.namespace):
            
            try:
                pm.namespace(rm=self.namespace)
                
            except RuntimeError as e:
                pm.warning('Could not remove namespace {0}'.format(self.namespace), e)
        
            
        
            
            
            
                
        
        
def show():
    win = RemapMaterialWidget(parent=maya_main_window())
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