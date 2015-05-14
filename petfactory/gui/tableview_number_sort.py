from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class NumberSortModel(QtGui.QSortFilterProxyModel):

    def lessThan(self, left, right):

        c = QtCore.QLocale(QtCore.QLocale.C)
        lvalue = c.toFloat(left.data())
        rvalue = c.toFloat(right.data())
        return lvalue < rvalue
  
  
class VrayIDWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(VrayIDWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300, 500)
        self.setWindowTitle('Vray ID')
        
        main_vbox = QtGui.QVBoxLayout()
        self.setLayout(main_vbox)
        
        # model
        self.model = QtGui.QStandardItemModel()
        
        self.proxy_model = NumberSortModel()
        self.proxy_model.setSourceModel(self.model)
  
        # tableview
        self.tableview = QtGui.QTableView()
        main_vbox.addWidget(self.tableview)
        self.tableview.setSortingEnabled(True)
        #self.tableview.setModel(self.model)
        self.tableview.setModel(self.proxy_model)
        
        # set horizontal header properties
        h_header = self.tableview.horizontalHeader()
        h_header.setStretchLastSection(True)
        
        # hide vertical header
        v_header = self.tableview.verticalHeader()
        v_header.setVisible(False)
        
        # set the font
        font = QtGui.QFont("Courier New", 12)
        self.tableview.setFont(font)
        
        # hide grid
        #self.tableview.setShowGrid(False)
        
        self.add_item()
        
    def add_item(self):
        
        for n in range(20):
            item = QtGui.QStandardItem(str(n))
            self.model.setItem(n, item)
        
def show():
    win = VrayIDWidget(parent=maya_main_window())
    win.show()
    return win


try:
    win.deleteLater()
    
except (RuntimeError, NameError):
    pass 
    
win = show()
win.move(60, 150)


#del(win)