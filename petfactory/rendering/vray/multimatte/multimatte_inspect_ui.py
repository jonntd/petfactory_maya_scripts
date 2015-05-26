from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import pymel.core as pm
import pprint


def inspect_mm():
    
    node_list = pm.ls()
    
    object_id_list = []
    mat_id_list = []
    op_id_list = []
    
    mat_id_dict = {}
    op_id_dict = {}
    object_id_dict = {}
    
    ret_dict = {}
    ret_dict['material_id'] = mat_id_dict
    ret_dict['object_properties_id'] = op_id_dict
    ret_dict['object_id'] = object_id_dict
    
    
    for node in node_list:
        
        if isinstance(node, pm.nodetypes.VRayObjectProperties):
            if node.objectIDEnabled.get():
                op_id_list.append(node)
            
        elif pm.attributeQuery('vrayObjectID', exists=True, node=node):
            object_id_list.append(node)
            
        elif pm.attributeQuery('vrayMaterialId', exists=True, node=node):
            mat_id_list.append(node)
            
    

    if object_id_list:
        for node in object_id_list:
            object_id_dict[node.name()] = node.vrayObjectID.get()


    if op_id_list:
        
        for node in op_id_list:
            op_id_dict[node.name()] = node.objectID.get()
       
    if mat_id_list:
        
        for node in mat_id_list:
            mat_id_dict[node.name()] = node.vrayMaterialId.get()


    return ret_dict
    
    
    
import petfactory.util.verify as pet_verify

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    

class MultimatteInspectWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(MultimatteInspectWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,400)
        self.setWindowTitle("Multimatte inspect")
        
        # layout
        main_vbox = QtGui.QVBoxLayout()
        self.setLayout(main_vbox)
        
        
        # models
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Multimatte ID', 'Type', 'Node'])
        
        # tableviews
        self.tableview = QtGui.QTableView()
        self.tableview.setModel(self.model)
        header = self.tableview.horizontalHeader()
        header.setStretchLastSection(True)
        main_vbox.addWidget(self.tableview)
        self.tableview.setSortingEnabled(True)
        
        self.populate_model()
        
        
    def populate_model(self):
        
        mm_dict = inspect_mm()
        
        self.item_from_dict(mm_dict, 'material_id')
        self.item_from_dict(mm_dict, 'object_properties_id')
        self.item_from_dict(mm_dict, 'object_id')
        
       
    def item_from_dict(self, mm_dict, key):
        
        mat_dict = mm_dict.get(key) 

        row = self.model.rowCount()
        for k, v in mat_dict.iteritems():
            
            item_id = QtGui.QStandardItem(str(v))
            item_id.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.model.setItem(row, 0, item_id)
            
            item_type = QtGui.QStandardItem(key)
            item_type.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.model.setItem(row, 1, item_type)
            
            item_node = QtGui.QStandardItem(str(k))
            item_node.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.model.setItem(row, 2, item_node)
            
            row += 1
            

           
def show():
    win = MultimatteInspectWidget(parent=maya_main_window())
    win.show()
    return win

try:
    win.close()
    
except NameError:
    pass
    

win = show()
win.move(100,150)