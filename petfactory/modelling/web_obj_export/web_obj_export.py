from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import pprint
import petfactory.gui.persistence as persistence

attrKey = 'objExportName'

 
def gather_meshes():
    
    mesh_list = pm.ls(type='mesh')
    match_list = []
    
    for mesh in mesh_list:
        
        if pm.attributeQuery(attrKey, node=mesh, exists=True):
            
            #attr = pm.getAttr('{}.{}'.format(mesh, attrKey))
            match_list.append(mesh)
            print('attr found on: {}'.format(mesh))
                
    return match_list


def addMeshAttr(attrValue):
    
    sel_list = pm.ls(sl=True)
    count = 0
    
    for sel in sel_list:
        
        try:
            shape = sel.getShape()
            
            # if the attr does not exist create it
            if not pm.attributeQuery(attrKey, node=shape, exists=True):
            
                pm.addAttr(shape, ln=attrKey, dt='string')
            
            pm.setAttr('{}.{}'.format(shape, attrKey), attrValue)
            count += 1
    
        except AttributeError as e:
            #print(e)
            pass
            
    print('the attr "{}" was set to: "{}" on {} meshe(s)'.format(attrKey, attrValue, count))
    

def export_mesh_with_attr(path):
    
    mesh_list = gather_meshes()
    
    mesh_attr_dict = {}
    export_mesh_list = []
    
    for mesh in mesh_list:
        
        attr = pm.getAttr('{}.{}'.format(mesh, attrKey))
        
        if attr not in mesh_attr_dict:
            mesh_attr_dict[attr] = []
            
        mesh_attr_dict[attr].append(mesh)
        
    #return mesh_attr_dict
    
    
    for attr, mesh_list in mesh_attr_dict.iteritems():
        
        dup_list = []
        #print(attr)
        for mesh in mesh_list:
            dup = mesh.duplicate()
            dup_list.append(dup)
        
        if len(dup_list) > 1:
            combined_mesh = pm.polyUnite(dup_list, n=attr, ch=False )[0]
        else:
            combined_mesh = dup_list[0]
            
        pm.polyTriangulate(combined_mesh, ch=False)
        export_mesh_list.append(combined_mesh)
        
        
    pm.select(export_mesh_list)
    pm.exportSelected(path, force=True, typ='OBJexport', op="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")
    
    #pm.delete()

    
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
class WebObjExportWidget(QtGui.QDialog):
    
    def __init__(self, parent=None):
        
        super(WebObjExportWidget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 300, 70)
        self.setWindowTitle("Web obj export")        
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        # set path        
        path_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(path_hbox)

        self.path_lineedit = QtGui.QLineEdit()
        path_hbox.addWidget(self.path_lineedit)
        
        set_path_btn = QtGui.QPushButton('Set path')
        path_hbox.addWidget(set_path_btn)        
        set_path_btn.setMaximumWidth(70)
        set_path_btn.clicked.connect(self.set_path_btn_clicked)
        
        # add name         
        name_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(name_hbox)

        self.name_lineedit = QtGui.QLineEdit()
        name_hbox.addWidget(self.name_lineedit)
        
        add_name_btn = QtGui.QPushButton('Add Name')
        name_hbox.addWidget(add_name_btn)        
        add_name_btn.setMaximumWidth(70)
        add_name_btn.clicked.connect(self.add_name_btn_clicked)
        
        #self.name_combobox = QtGui.QComboBox()
        #name_hbox.addWidget(self.name_combobox)
        #self.name_combobox.addItems(['apa', 'katt'])
        
        export_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(export_hbox)
        
        
        # preview 
        preview_btn = QtGui.QPushButton('Preview')
        export_hbox.addWidget(preview_btn)
        preview_btn.clicked.connect(self.preview_btn_clicked) 
        
        # export 
        export_btn = QtGui.QPushButton('Export')
        export_hbox.addWidget(export_btn)
        export_btn.clicked.connect(self.export_btn_clicked) 
        
        vbox.addStretch()   
        self.show()
        
    def add_name_btn_clicked(self):
        
        name = self.name_lineedit.text()
        
        if len(name) > 0:
            addMeshAttr(name)
    
    def preview_btn_clicked(self):
        
        match_list = gather_meshes()
        pprint.pprint(match_list)
        pm.select(match_list)
    
    def set_path_btn_clicked(self):
        
        path = persistence.select_dir('Select export directory')
        
        if path:
            self.path_lineedit.setText(path)
        #self.path_lineedit.setText('apapapappa')
         
                
    def export_btn_clicked(self):
        
        path = self.path_lineedit.text()
        
        if os.path.isdir(path):
            file_name = 'house.obj'
            export_mesh_with_attr(os.path.join(path, file_name))
        
        
        
def show():
    win = WebObjExportWidget(parent=maya_main_window())
    win.show()
    
#show()