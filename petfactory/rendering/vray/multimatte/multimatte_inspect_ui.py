from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import pymel.core as pm
import pprint

import petfactory.util.verify as pet_verify

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
    
    

class NumberSortModel(QtGui.QSortFilterProxyModel):

    def lessThan(self, left, right):
        
        if left.column() == 0:
            c = QtCore.QLocale(QtCore.QLocale.C)
            lvalue = c.toFloat(left.data())
            rvalue = c.toFloat(right.data())
        
        else:
            lvalue = left.data()
            rvalue = right.data()
        
        return lvalue < rvalue
        
        
class MultimatteInspectWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(MultimatteInspectWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(400,400)
        self.setWindowTitle("Multimatte inspect")
        
        # layout
        main_vbox = QtGui.QVBoxLayout()
        self.setLayout(main_vbox)
        
        
        # models
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['ID', ' ID Type', 'Node'])
        
        self.model.dataChanged.connect(self.data_changed)
        
        self.proxy_model = NumberSortModel()
        self.proxy_model.setSourceModel(self.model)
        
        # tableviews
        self.tableview = QtGui.QTableView()
        header = self.tableview.horizontalHeader()
        header.setStretchLastSection(True)
        main_vbox.addWidget(self.tableview)
        self.tableview.setModel(self.proxy_model)
        self.tableview.setSortingEnabled(True)
        
        self.tableview.doubleClicked.connect(self.tableview_doubleclicked)
        
        self.tableview.setColumnWidth(0,50)
        self.tableview.setColumnWidth(1,140)
        
        v_header = self.tableview.verticalHeader()
        v_header.setVisible(False)
        
        #self.populate_model()
        
        refresh_button = QtGui.QPushButton('Refresh')
        refresh_button.clicked.connect(self.refresh_button_clicked)
        main_vbox.addWidget(refresh_button)
            
        
    def refresh_button_clicked(self):
             
        self.populate_model()
                
    def data_changed(self, topLeft, bottomRight):
        
        #self.model.blockSignals(True)
        
        # get the row that was changed, from the proxy model
        row = topLeft.row()
        
        # remap the index from the proxymodel to the source model
        index = self.proxy_model.mapToSource(topLeft)
        
        # get the node text
        item_node = self.model.item(row, 2)
        
        node_type = node = None
        
        if item_node is not None:
            node_string = item_node.text()
            node = pet_verify.to_pynode(node_string)
        
        # get the node text
        node_type_item = self.model.item(row, 1)
        
        if node_type_item is not None:        
            node_type = node_type_item.text()

        
        if node is not None and node_type is not None:
            print(node, node_type)
        
        #self.model.blockSignals(False)
        
        
    def tableview_doubleclicked(self, proxy_index):
        
        index = self.proxy_model.mapToSource(proxy_index)
        
        col = index.column()
        
        # if we did not click column 2 return
        if col != 2:
            return
            
        row = index.row()
        
        item = self.model.item(row, col)
        node_string = item.text()
        
        node = pet_verify.to_pynode(node_string)
        
        if node is None:
            return
            
        pm.select(node)

           
    def populate_model(self):
        
        self.model.removeRows(0, self.model.rowCount())        
        
        mm_dict = inspect_mm()
        
        material_id_dict = mm_dict.get('material_id')
        object_properties_id_dict = mm_dict.get('object_properties_id') 
        object_id_dict = mm_dict.get('object_id') 
        
        id_list = material_id_dict.values()
        id_list.extend(object_properties_id_dict.values())
        id_list.extend(object_id_dict.values())
        
        
        id_duplicates = list(set([id for id in id_list if id_list.count(id) > 1]))
        
        self.item_from_dict(material_id_dict, 'material', id_duplicates)
        self.item_from_dict(object_properties_id_dict, 'object properties', id_duplicates)
        self.item_from_dict(object_id_dict, 'object', id_duplicates)
        
        # sort the table view
        self.tableview.sortByColumn(0, QtCore.Qt.AscendingOrder)
                
        
       
    def item_from_dict(self, mm_dict, type, id_duplicates):
        
        #print(mm_dict, type)
        row = self.model.rowCount()        
        
        for k, v in mm_dict.iteritems():
            
            item_id = QtGui.QStandardItem(str(v))
            item_id.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            self.model.setItem(row, 0, item_id)
            
            if v in id_duplicates:
                item_id.setBackground(QtGui.QBrush(QtGui.QColor(50, 103, 118), QtCore.Qt.SolidPattern))
                

            item_type = QtGui.QStandardItem(type)
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