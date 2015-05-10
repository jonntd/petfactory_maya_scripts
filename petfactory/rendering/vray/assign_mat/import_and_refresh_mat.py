from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial

import petfactory.util.verify as pet_verify

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
    
class ImportMaterialWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
 
        self.curr_mat_list = None
        self.import_mat_list = None
        
        super(ImportMaterialWidget, self).__init__(parent)
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
        
        self.add_current_mat_button = QtGui.QPushButton('Add current mat')
        self.add_current_mat_button.clicked.connect(self.add_mat)
        main_vbox.addWidget(self.add_current_mat_button)
        
        
        self.import_mat_button = QtGui.QPushButton('Import mat')
        self.import_mat_button.clicked.connect(self.import_mat)
        main_vbox.addWidget(self.import_mat_button )
        
        
        #self.add_mat()
    
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
            
        import_file = self.open_file(title='apa', filter='Maya (*.mb *.ma)')
                
        
    def open_file(self, title, filter):
    
        file_name, selected_filter = QtGui.QFileDialog.getOpenFileName(None, title, None, filter)
        
        if file_name:
            
            ns = 'lookdev'
            pm.importFile(file_name, namespace=ns)
            
            mat_list_import = [m for m in pm.ls(mat=True) if m.name() not in ['lambert1', 'particleCloud1']]

            
            mat_list_import_set = set(mat_list_import)
            curr_mat_list_set = set(self.curr_mat_list)            
            diff_set = mat_list_import_set.difference(curr_mat_list_set)
            
            for d in diff_set:
                import_short_name = d.split(':')[-1]
                #print(import_short_name)
                        

        
def show():
    win = ImportMaterialWidget(parent=maya_main_window())
    win.show()
    return win


try:
    win.close()
    
except NameError:
    pass
    

win = show()
win.move(100,150)