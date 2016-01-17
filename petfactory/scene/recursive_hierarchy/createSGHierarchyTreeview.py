 # -*- coding: utf-8 -*-
 
import xml.etree.ElementTree as ET
import xml.dom.minidom
import pymel.core as pm
from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pprint
from functools import partial

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
def recurseHierarchy(mayaNode, xmlParent):
    
    xmlNode = ET.Element('node')
    xmlNode.set('name', mayaNode.name())
    xmlNode.set('nodeType', 'group')
    xmlNode.set('prefix', 'INT')
    xmlNode.set('sectionInSGUI', '1')
    xmlParent.append(xmlNode)
    
    numChildren = mayaNode.numChildren()
    print(numChildren)
    if numChildren > 0:
        
        children = mayaNode.getChildren()
        for child in children:
            print(child)
            recurseHierarchy(child, xmlNode)

def exportHierarchyXML():
    
    sel = pm.ls(sl=True)
    if len(sel) < 1:
        print('Nothing is selected!')
        return
        
    mayaNode = sel[0]
    xmlRoot = ET.Element('root')
    recurseHierarchy(mayaNode, xmlRoot)
    xmlString = ET.tostring(xmlRoot)
    miniDomXml = xml.dom.minidom.parseString(xmlString)
    prettyXML = miniDomXml.toprettyxml()
    
    fname, _ = QtGui.QFileDialog.getSaveFileName(caption='Save XML', directory='/home', filter='*.xml')

    if(fname):
        f = open(fname,'w')
        f.write(prettyXML)
        f.close()
    

class UI(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(UI, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,500)
        self.setWindowTitle("UI")
        
        # main layout
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(mainLayout)
        
        self.menubar = QtGui.QMenuBar()
        mainLayout.addWidget(self.menubar)
        fileMenu = self.menubar.addMenu('File')
 
        # save 
        self.saveXMLAction = QtGui.QAction('Save XML', self)
        self.saveXMLAction.triggered.connect(self.saveXML)
        fileMenu.addAction(self.saveXMLAction)
        
        # load
        self.loadXMLAction = QtGui.QAction('Load XML', self)
        self.loadXMLAction.triggered.connect(self.loadXML)
        fileMenu.addAction(self.loadXMLAction)
        
        
        # load
        self.fromSceneGraphAction = QtGui.QAction('Export SceneGraph', self)
        self.fromSceneGraphAction.triggered.connect(exportHierarchyXML)
        fileMenu.addAction(self.fromSceneGraphAction)
        
        
        
       
        # layout
        vbox = QtGui.QVBoxLayout()
        vbox.setContentsMargins(6,6,6,6)
        mainLayout.addLayout(vbox)
        
        # treeview
        self.treeview = QtGui.QTreeView()
        vbox.addWidget(self.treeview)
        self.treeview.setHeaderHidden(True)
        self.treeview.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        
        self.setStyleSheet()

        # model
        self.model = QtGui.QStandardItemModel()
        self.treeview.setModel(self.model)
        
        # set node type button
        node_type_btn_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(node_type_btn_hbox)
        
        set_group_btn = QtGui.QPushButton('Group')
        node_type_btn_hbox.addWidget(set_group_btn)
        set_group_btn.clicked.connect(partial(self.change_node_type, 'group'))
        
        set_switch_btn = QtGui.QPushButton('Switch')
        node_type_btn_hbox.addWidget(set_switch_btn)
        set_switch_btn.clicked.connect(partial(self.change_node_type, 'switch'))
        
        
        # add / remove button
        add_remove_btn_hbox = QtGui.QHBoxLayout()
        vbox.addLayout(add_remove_btn_hbox)
        
        add_btn = QtGui.QPushButton('+')
        add_remove_btn_hbox.addWidget(add_btn)
        add_btn.clicked.connect(self.add_btn_clicked)
        
        remove_btn = QtGui.QPushButton('-')
        add_remove_btn_hbox.addWidget(remove_btn)
        remove_btn.clicked.connect(self.remove_btn_clicked)
        
        
    def change_node_type(self, nodeType):
        
        if(self.treeview.selectionModel().hasSelection()):
            
            for index in self.treeview.selectedIndexes():
                item = self.model.itemFromIndex(index)
                self.setNodeType([item],nodeType )
        else:
            print('Nothin is selected!')
                
                
    def loadXML(self):
                
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, caption='Load XML', directory='/home', filter='*.xml')

        if(fname):
            f = open(fname, 'r')
            data = f.read()
            f.close()
            
            tree = ET.fromstring(data)
            xml_recurse_pyside(tree, win.get_root_item())
            
                        
    def saveXML(self):

        if(self.treeview.selectionModel().hasSelection()):

            for index in self.treeview.selectedIndexes():

                row = index.row()
                item = self.model.itemFromIndex(index)

                xmlRoot = ET.Element('root')                
                self.exportTreviewXML(item, -1, xmlRoot)
                xmlString = ET.tostring(xmlRoot)
                miniDomXml = xml.dom.minidom.parseString(xmlString)
                pp = miniDomXml.toprettyxml()
                
                
                fname, _ = QtGui.QFileDialog.getSaveFileName(self, caption='Save XML', directory='/home', filter='*.xml')

                if(fname):
                    f = open(fname,'w')
                    f.write(pp) # python will convert \n to os.linesep
                    f.close() # you can omit in most cases as the destructor will call if


    def setNodeType(self, itemList, nodeType):
        
        for item in itemList:
            
            item.setData(nodeType, role=QtCore.Qt.UserRole + 1)
            
            color = QtGui.QColor()
    
            if nodeType == 'group':        
                color.setRgbF(.6,.6,.6)
        
            elif nodeType == 'switch':
                color.setRgbF(1,.8,0)
        
            pixmap = QtGui.QPixmap(8, 8)
            pixmap.fill(QtGui.QColor(color))
            icon = QtGui.QIcon(pixmap)        
            item.setIcon(icon)
            
    
    def exportTreviewXML(self, item, depth, parent):
        
        name = item.text()
        nodeType = item.data(role=QtCore.Qt.UserRole + 1)
        #print('{}{}'.format('\t'*depth, name))
        depth += 1
        
        xmlNode = ET.Element('node')
        xmlNode.set('name', name)
        xmlNode.set('nodeType', str(nodeType))
        xmlNode.set('prefix', 'INT')
        xmlNode.set('sectionInSGUI', '0')

        
        if parent is not None:
            parent.append(xmlNode)

        if item.hasChildren():
            for i in range(item.rowCount()):
                child = item.child(i)
                self.exportTreviewXML(child, depth, xmlNode)
                
                
                                                            
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
    
    def add_btn_clicked(self):

        if(self.treeview.selectionModel().hasSelection()):
            
            for index in self.treeview.selectedIndexes():
                item = self.model.itemFromIndex(index)
        else:
            item = self.model.invisibleRootItem()

        newItem = QtGui.QStandardItem('New Item')
        newItem.setData('group', role=QtCore.Qt.UserRole + 1)
        
        color = QtGui.QColor()
        color.setRgbF(.6,.6,.6)        
        pixmap = QtGui.QPixmap(8, 8)
        pixmap.fill(QtGui.QColor(color))
        icon = QtGui.QIcon(pixmap)        
        newItem.setIcon(icon)
        
        item.appendRow(newItem)


    def remove_btn_clicked(self):

        if(self.treeview.selectionModel().hasSelection()):

            for index in self.treeview.selectedIndexes():

                row = index.row()
                item = self.model.itemFromIndex(index)
                parent = item.parent()

                parent_index = self.model.indexFromItem(parent)
                self.model.removeRow(row, parent_index)

        
    def setStyleSheet(self):

        #font = QtGui.QFont()
        #font.setPixelSize(15)
        #self.treeview.setFont(font)

        styleSheet = '''
        QTreeView::item {
            color: grey;
            font-size: 34px;
        }'''
        
        self.treeview.setStyleSheet(styleSheet)
        
def xml_recurse_pyside(xml_node, parent=None, depth=-1):

    name = xml_node.get('name') 
    node_type = xml_node.get('nodeType')
    node = QtGui.QStandardItem(name)
    #node.setSizeHint(QtCore.QSize(10,18))
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


#path = r'/Users/johan/Dev/maya/petfactory_maya_scripts/petfactory/scene/recursive_hierarchy/test.xml'
#path = r'/Users/johan/Dev/maya/petfactory_maya_scripts/petfactory/scene/recursive_hierarchy/nodeWithAttrib.xml'
#valid_types = ['group', 'switch']

#tree = ET.parse(path)
#root = tree.getroot()
#xml_recurse_pyside(root, win.get_root_item())
