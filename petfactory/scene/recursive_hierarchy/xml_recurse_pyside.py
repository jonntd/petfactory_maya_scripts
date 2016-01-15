import xml.etree.ElementTree as ET
import pymel.core as pm
from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pprint

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class UI(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(UI, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,500)
        self.setWindowTitle("UI")
 
        # layout
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        
        # treeview
        self.treeview = QtGui.QTreeView()
        vbox.addWidget(self.treeview)
        self.treeview.setHeaderHidden(True)
        self.treeview.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        # model
        self.model = QtGui.QStandardItemModel()
        self.treeview.setModel(self.model)
        
        # button
        node_type_btn_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(node_type_btn_hbox)
        
        set_group_btn = QtGui.QPushButton('Group')
        node_type_btn_hbox.addWidget(set_group_btn)
        set_group_btn.clicked.connect(self.change_node_type)
        
        set_switch_btn = QtGui.QPushButton('Switch')
        node_type_btn_hbox.addWidget(set_switch_btn)
        set_switch_btn.clicked.connect(self.change_node_type)
        
        
        # button
        print_btn = QtGui.QPushButton('Print')
        vbox.addWidget(print_btn)
        print_btn.clicked.connect(self.print_btn_clicked)
        
    def change_node_type(self):
        pass
        
    def print_btn_clicked(self):
        root = self.model.invisibleRootItem()
        ret_dict = {}
        self.recurse(root, -1, ret_dict)
        #pprint.pprint(ret_dict)
        
    def recurse(self, item, depth, ret_dict):

        # returns the number of child item rows that the item has.
        for i in range(item.rowCount()):
            child = item.child(i)
            node_type = child.data(role=QtCore.Qt.UserRole + 1)
            
            
            if child.hasChildren():
                depth += 1
                print('{}{}({})'.format('\t'*depth, child.text(), node_type))
                cd = {}
                ret_dict.update({child.text():cd})
                self.recurse(child, depth, cd)

            else:
                depth += 1
                print('{}{}({})'.format('\t'*depth, child.text(), node_type))
                ret_dict.update({child.text():[]})

            depth -= 1
               
    def get_root_item(self):
        return self.model.invisibleRootItem()
        
    def add_item(self, item):
        root_item = self.model.invisibleRootItem()
        root_item.appendRow(item)
        
              
def xml_recurse_pyside(xml_node, parent=None, depth=-1):

    name = xml_node.get('name') 
    node_type = xml_node.get('type')
    node = QtGui.QStandardItem(name)
    node.setSizeHint(QtCore.QSize(10,16))
    node.setData(node_type, role=QtCore.Qt.UserRole + 1)
       
    color = QtGui.QColor()
    
    if node_type == 'group':        
        color.setRgbF(.6,.6,.6)
        
    elif node_type == 'switch':
        color.setRgbF(1,.8,0)
        
    pixmap = QtGui.QPixmap(8, 8)
    pixmap.fill(QtGui.QColor(color))
    icon = QtGui.QIcon(pixmap)        
    node.setIcon(icon)
    
    if parent:
        parent.appendRow(node)
        
    print('{} {} {}'.format(depth*'\t', name, node_type))
    
    depth += 1

    if node_type not in valid_types:
        print('not a valid type, raise error!')
        
    children = xml_node.getchildren()

    if children:
        for child in children:
            xml_recurse_pyside(child, node, depth)


try:
    win.close()
    
except NameError:
    print('No win to close')
    
win = UI(parent=maya_main_window())
win.show()
win.move(100,150)


path = r'/Users/johan/Dev/maya/petfactory_maya_scripts/petfactory/scene/recursive_hierarchy/test.xml'
valid_types = ['group', 'switch']

tree = ET.parse(path)
root = tree.getroot()

xml_recurse_pyside(root, win.get_root_item())
