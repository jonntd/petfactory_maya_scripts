from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui

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
        main_vbox.setContentsMargins(0,0,0,0)
        self.setLayout(main_vbox)
        
        
        # models
        self.curr_mat_model = QtGui.QStandardItemModel()
        self.new_mat_model = QtGui.QStandardItemModel()
        
        # tableview layout
        tableview_hbox = QtGui.QHBoxLayout()
        tableview_hbox.setContentsMargins(0,0,0,0)
        main_vbox.addLayout(tableview_hbox)
        
        # tableviews
        
        # curr mat
        self.curr_mat_tableview = QtGui.QTableView()
        self.curr_mat_tableview.setModel(self.curr_mat_model)
        
        # new mat
        self.new_mat_tableview = QtGui.QTableView()
        self.new_mat_tableview.setModel(self.new_mat_model)
        self.new_mat_tableview.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        
        
        # assign button
        self.assign_button = QtGui.QPushButton('<<')
        self.assign_button.setFixedWidth(25)
        self.assign_button.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.assign_button.clicked.connect(self.assign_button_clicked)
        
        # add the widgets
        tableview_hbox.addWidget(self.curr_mat_tableview)
        tableview_hbox.addWidget(self.assign_button)
        tableview_hbox.addWidget(self.new_mat_tableview)
        
        
        
    def assign_button_clicked(self):
        
        curr_mat_selection_model = self.curr_mat_tableview.selectionModel()
        curr_mat_selected_indexes = curr_mat_selection_model.selectedIndexes()
        
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
        
        
        curr_mat_list = []
        for index in curr_mat_selected_indexes:
            curr_mat = self.curr_mat_model.itemFromIndex(index)
            curr_mat_list.append(curr_mat)
            
            
        for curr_mat in curr_mat_list:
            
            curr_mat_node = pet_verify.to_pynode(curr_mat.text())
        
            if curr_mat_node is None:
                pm.warning('The current mat is not a valid PyNode')
                curr_mat.setText('not a valid material')
                continue
            
            
            curr_mat.setText(new_mat.text())
            
            print(curr_mat_node, new_mat_node)
            
        
        
        
         
    def add_selected_mat(self, model):
        
        sel_list = pm.ls(sl=True)
        
        items = []
        for sel in sel_list:
            items.append(QtGui.QStandardItem(sel.name()))
            
        self.add_to_model(model, items)
        
    def add_to_model(self, model, items):
                
        num_rows = model.rowCount()
        
        for index, item in enumerate(items):
            model.insertRow(num_rows+index, item)
        
        
        
        
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


curr_mat_list = [pm.PyNode('blinn{0}'.format(n+1)) for n in range(3)]
new_mat_list = [pm.PyNode('lambert{0}'.format(n+2)) for n in range(3)]

pm.select(curr_mat_list)
win.add_selected_mat(win.curr_mat_model)

pm.select(new_mat_list)
win.add_selected_mat(win.new_mat_model)

