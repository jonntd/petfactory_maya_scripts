from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial

import petfactory.util.verify as pet_verify

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class ReassignMatWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(ReassignMatWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,400)
        self.setWindowTitle("Reassign materials")
        
        # layout
        main_vbox = QtGui.QVBoxLayout()
        main_vbox.setContentsMargins(5,5,5,5)
        self.setLayout(main_vbox)
        
        
        # models
        self.curr_mat_model = QtGui.QStandardItemModel()
        self.curr_mat_model.setHorizontalHeaderLabels(['Current Material', 'Class'])
        
        self.new_mat_model = QtGui.QStandardItemModel()
        self.new_mat_model.setHorizontalHeaderLabels(['New Material'])
        
        
        # tableview layout
        tableview_hbox = QtGui.QHBoxLayout()
        tableview_hbox.setContentsMargins(0,0,0,0)
        main_vbox.addLayout(tableview_hbox)
        
        
        
        # tableviews
        
        # curr mat layout
        curr_mat_tableview_vbox = QtGui.QVBoxLayout()
        curr_mat_tableview_vbox.setContentsMargins(0,0,0,0)
        tableview_hbox.addLayout(curr_mat_tableview_vbox)
        
        # curr mat tableview
        self.curr_mat_tableview = QtGui.QTableView()
        self.curr_mat_tableview.doubleClicked.connect(self.tableview_double_clicked)
        self.curr_mat_tableview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.curr_mat_tableview.setModel(self.curr_mat_model)
        curr_mat_header = self.curr_mat_tableview.horizontalHeader()
        curr_mat_header.setStretchLastSection(True)
        curr_mat_tableview_vbox.addWidget(self.curr_mat_tableview)
        
        
        
        # load curr materials
        add_rem_curr_mat_hbox = QtGui.QHBoxLayout()
        curr_mat_tableview_vbox.addLayout(add_rem_curr_mat_hbox)
        self.add_to_curr_table_view_button = QtGui.QPushButton('+')
        self.add_to_curr_table_view_button.clicked.connect(partial(self.add_items, self.curr_mat_tableview))
        self.add_to_curr_table_view_button.setFixedWidth(40)
        self.rem_to_curr_table_view_button = QtGui.QPushButton('-')
        self.rem_to_curr_table_view_button.clicked.connect(partial(self.remove_items, self.curr_mat_tableview))
        self.rem_to_curr_table_view_button.setFixedWidth(40)
        add_rem_curr_mat_hbox.addWidget(self.add_to_curr_table_view_button)
        add_rem_curr_mat_hbox.addWidget(self.rem_to_curr_table_view_button)
        add_rem_curr_mat_hbox.addStretch()
        
        
        
        # assign button
        self.assign_button = QtGui.QPushButton('<')
        self.assign_button.setFixedWidth(25)
        self.assign_button.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.assign_button.clicked.connect(self.assign_button_clicked)
        tableview_hbox.addWidget(self.assign_button)
        

        # new mat
        
        # new mat layout
        new_mat_tableview_vbox = QtGui.QVBoxLayout()
        new_mat_tableview_vbox.setContentsMargins(0,0,0,0)
        tableview_hbox.addLayout(new_mat_tableview_vbox)
        
        self.new_mat_tableview = QtGui.QTableView()
        self.new_mat_tableview.doubleClicked.connect(self.tableview_double_clicked)
        self.new_mat_tableview.setModel(self.new_mat_model)
        #self.new_mat_tableview.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        new_mat_header = self.new_mat_tableview.horizontalHeader()
        new_mat_header.setStretchLastSection(True)
        new_mat_tableview_vbox.addWidget(self.new_mat_tableview)
        
        
        
        # load new materials
        add_rem_new_mat_hbox = QtGui.QHBoxLayout()
        new_mat_tableview_vbox.addLayout(add_rem_new_mat_hbox)
        self.add_to_new_table_view_button = QtGui.QPushButton('+')
        self.add_to_new_table_view_button.clicked.connect(partial(self.add_items, self.new_mat_tableview))
        self.add_to_new_table_view_button.setFixedWidth(40)
        self.rem_to_new_table_view_button = QtGui.QPushButton('-')
        self.rem_to_new_table_view_button.clicked.connect(partial(self.remove_items, self.new_mat_tableview))
        self.rem_to_new_table_view_button.setFixedWidth(40)
        add_rem_new_mat_hbox.addWidget(self.add_to_new_table_view_button)
        add_rem_new_mat_hbox.addWidget(self.rem_to_new_table_view_button)
        add_rem_new_mat_hbox.addStretch()

                
        
    def tableview_double_clicked(self, index):
        
        col = index.column()
        
        # return if the second column was double clicked
        if col == 1:
            return
        
        model = index.model()
        mat_node = pet_verify.to_pynode(index.data())
        
        if mat_node:
            pm.select(mat_node)
                  
    
    def add_items(self, tableview):
        
        selection_model = tableview.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        model = tableview.model()
        
        self.add_selected_mat(model)

       
            
    def remove_items(self, tableview):
        
        selection_model = tableview.selectionModel()
        #selected_indexes = selection_model.selectedIndexes()
        selected_rows = selection_model.selectedRows()
        model = tableview.model()
        
        
        row_list = [sel.row() for sel in selected_rows]
        row_list.sort(reverse=True)
        
        for row in row_list:
            model.removeRow(row)
                            
        
    def assign_button_clicked(self):
        
        curr_mat_selection_model = self.curr_mat_tableview.selectionModel()
        curr_mat_selected_indexes = curr_mat_selection_model.selectedRows(0)
        
        #curr_mat_selected_indexes = curr_mat_selection_model.selectedIndexes()
        
        new_mat_selection_model = self.new_mat_tableview.selectionModel()
        new_mat_selected_indexes = new_mat_selection_model.selectedIndexes()
        
        
        if len(curr_mat_selected_indexes) < 1:
            pm.warning('Select a current material')
            return
            
        if len(new_mat_selected_indexes) < 1:
            pm.warning('Select a new material')
            return
        
        # use the new mat that was selected first (if cmd clicked)
        new_mat = self.new_mat_model.itemFromIndex(new_mat_selected_indexes[0])
        new_mat_node = pet_verify.to_pynode(new_mat.text())
        
        if new_mat_node is None:
            pm.warning('The new mat is not a valid PyNode')
            return
            
            
            
        # get the shading group
        new_mat_sg_list = new_mat_node.listConnections(type='shadingEngine')
        
        # get the node type
        nodetype = type(new_mat_node).nodeType(new_mat_node)
        
        if len(new_mat_sg_list) < 1:

            #sg = pm.createNode('shadingEngine')
            sg = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='{0}SG'.format(new_mat.text()))
            new_mat_node.outColor >> sg.surfaceShader
            new_mat_sg = sg
            
        else:
            new_mat_sg = new_mat_sg_list[0]
            
        '''    
        curr_mat_list = []
        for index in curr_mat_selected_indexes:
            curr_mat = self.curr_mat_model.itemFromIndex(index)
            curr_mat_list.append(curr_mat)
        '''
            
            
        #for curr_mat in curr_mat_list:
        for index in curr_mat_selected_indexes:
            
            curr_mat = self.curr_mat_model.itemFromIndex(index)            
            row = curr_mat.row()
            
            curr_class_item = self.curr_mat_model.item(row, 1)
            
            curr_mat_node = pet_verify.to_pynode(curr_mat.text())
        
            if curr_mat_node is None:
                pm.warning('The current mat is not a valid PyNode')
                curr_mat.setText('not a valid material')
                continue
            
            
            curr_mat.setText(new_mat.text())
            curr_class_item.setText(nodetype)
            
            
            #print(curr_mat_node, new_mat_node)
            
            
            # get the shading group
            sg_list = curr_mat_node.listConnections(type='shadingEngine')
            
            if len(sg_list) < 1:
                continue
                
            #print(sg_list)
            
            
            mesh_list = []
            face_list = []
        
             
            # loop through the sg looking for menbers
            for sg in sg_list:
                
                member_list = sg.members(flatten=True)
                
                # loop through the members, check it the mat is assigned to faces or meshes
                for member in member_list:
        
                    if type(member) == pm.nodetypes.Mesh:
                        #print('mashhh')
                        mesh_list.append(member)
                        
                    elif type(member) == pm.general.MeshFace:
                        #print('face')
                        face_list.append(member)
            
            
            
            # reassign the mat
            
            if len(mesh_list) > 0:
                pm.sets(new_mat_sg, forceElement=mesh_list)
                
            else:
                #pm.warning('{0} is not assigned to a mesh'.format(curr_mat.text()))
                pass
        
        
        
         
    def add_selected_mat(self, model):
        
        num_rows = model.rowCount()
        
        sel_list = pm.ls(sl=True)
        
        #items = []
        for n, sel in enumerate(sel_list):
            
            item = QtGui.QStandardItem(sel.name())
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            model.setItem(num_rows+n, 0, item)
            
            if model == self.curr_mat_model:
                
                #print(dir(type(sel)))
                nodetype = type(sel).nodeType(sel)
                
                item = QtGui.QStandardItem(nodetype)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                model.setItem(num_rows+n, 1, item)
                
            #items.append(item)
            
        #self.add_to_model(model, items)
    ''' 
    def add_to_model(self, model, items):
                
        num_rows = model.rowCount()
        
        for index, item in enumerate(items):
            model.insertRow(num_rows+index, item)
    '''
        
        
        
        
def show():
    win = ReassignMatWidget(parent=maya_main_window())
    win.show()
    return win


try:
    win.close()
    
except NameError:
    pass
    

win = show()
win.move(100,150)


#pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/rgb_cmy_mat.mb', f=True)
#curr_mat_list = [pm.PyNode('blinn{0}'.format(n+1)) for n in range(3)]
#new_mat_list = [pm.PyNode('lambert{0}'.format(n+2)) for n in range(3)]

#pm.select(curr_mat_list)
#win.add_selected_mat(win.curr_mat_model)

#pm.select(new_mat_list)
#win.add_selected_mat(win.new_mat_model)

