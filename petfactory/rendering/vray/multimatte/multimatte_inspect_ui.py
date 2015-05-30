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
    
    

class MyDelegate(QtGui.QItemDelegate):
    
    def __init__(self, parent=None):
        super(MyDelegate, self).__init__(parent)
        
    def createEditor(self, parent, option, index):
        
        col = index.column()
        
        if col == 0:

            spinbox = QtGui.QSpinBox(parent)
            spinbox.setRange(0, 9999)
            spinbox.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            return spinbox
        
        else:
            return QtGui.QLineEdit(parent)
            
            
    def setModelData(self, editor, model, index):
        
        row = index.row()
        col = index.column()
        
        if col == 0:
           
            # remp the index                 
            source_index = model.mapToSource(index)
            source_model = model.sourceModel()
            
            source_row = source_index.row()
            num_rows = source_model.rowCount()
            
            old_value = int(index.data())
            value = editor.value()
            
            # get the type and node strings
            node_string = source_model.index(source_row, 2).data()
            id_type_string = source_model.index(source_row, 1).data()
            
            # try to construct a PyNode
            pynode = pet_verify.to_pynode(node_string)
            if pynode is not None:
                
                if id_type_string == 'object':
                    pynode.vrayObjectID.set(value)                    
                    
                elif id_type_string == 'object properties':
                    pynode.objectID.set(value)
                    
                elif id_type_string == 'material':
                    pynode.vrayMaterialId.set(value)
                
                # change the data in the model
                model.setData(index, value)
                
                # look for duplicates
                value_list = [ int(source_model.index(row, 0).data()) for row in range(num_rows)]
                count_new_id = value_list.count(value)
                count_old_id = value_list.count(old_value)
                
                # no duplicates
                if count_new_id == 1:
                    
                    item = source_model.itemFromIndex(source_index)
                    item.setBackground(QtGui.QBrush())

                else:                 
                
                    for row in range(num_rows):
                                                
                        i = model.index(row, 0)
                        v = int(i.data())
                                                
                        if v == value:
                            item = source_model.itemFromIndex(model.mapToSource(i))
                            item.setBackground(QtGui.QBrush(QtGui.QColor(150, 43, 118), QtCore.Qt.SolidPattern))                    
               
                
                # reset the bg color of items that hade the same id of the item that was changed,
                # but is unique after the current item was changed
                if count_old_id == 1:
                    
                    for row in range(num_rows):
                                                
                        i = model.index(row, 0)
                        v = int(i.data())
                                                
                        if v == old_value:
                            item = source_model.itemFromIndex(model.mapToSource(i))
                            item.setBackground(QtGui.QBrush()) 

                
            else:
                pm.warning('Could not set the V-Ray ID')
                return
            
        
        else:
            model.setData(index, editor.value())

        
class NumberSortModel(QtGui.QSortFilterProxyModel):

    def lessThan(self, left, right):

        if left.column() == 0:
            
            c = QtCore.QLocale(QtCore.QLocale.C)
            lvalue = c.toFloat(str(left.data()))
            rvalue = c.toFloat(str(right.data()))
            
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
        #self.model.dataChanged.connect(self.data_changed)        
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
        
        self.tableview.setAlternatingRowColors(True)
        
        self.tableview.setColumnWidth(0,60)
        self.tableview.setColumnWidth(1,140)
        
        self.tableview.setItemDelegate(MyDelegate(self.tableview))
        
        
        v_header = self.tableview.verticalHeader()
        v_header.setVisible(False)
        
        #self.populate_model()
        
        refresh_button = QtGui.QPushButton('Refresh')
        refresh_button.clicked.connect(self.refresh_button_clicked)
        main_vbox.addWidget(refresh_button)
            
        
    def refresh_button_clicked(self):
             
        self.populate_model()
                     
        
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
        
        row = self.model.rowCount()        
        
        for k, v in mm_dict.iteritems():
            
            item_id = QtGui.QStandardItem(str(v))
            item_id.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            self.model.setItem(row, 0, item_id)
            
            if v in id_duplicates:
                item_id.setBackground(QtGui.QBrush(QtGui.QColor(150, 43, 118), QtCore.Qt.SolidPattern))
                

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