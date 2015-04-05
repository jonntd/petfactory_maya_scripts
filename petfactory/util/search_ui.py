from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import re
import pymel.core as pm

import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

import petfactory.util.search as pet_search
reload(pet_search)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
  
class RegexWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(RegexWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        # layout
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)
        
        self.resize(300,100)
        self.setWindowTitle("Regex set")
        
        self.regex_lineedit = simple_widget.labeled_lineedit(label='Regex', parent_layout=vertical_layout)
        self.regex_lineedit.setText('^[\w\d|]*xxx[\w\d|]*$')
        self.set_name_lineedit = simple_widget.labeled_lineedit(label='Set name', parent_layout=vertical_layout)
        
        self.use_parent_checkbox = simple_widget.labeled_checkbox(label='Use parent', parent_layout=vertical_layout)
        self.use_longname_checkbox = simple_widget.labeled_checkbox(label='Use long name', parent_layout=vertical_layout)
        
        self.nodetype_dict = {  'Mesh':pm.nodetypes.Mesh,
                                'NurbsCurve':pm.nodetypes.NurbsCurve,
                                'NurbsSurface':pm.nodetypes.NurbsSurface}
        nodetype_keys = self.nodetype_dict.keys()
        nodetype_keys.sort()
        
        self.nodetype_combobox = simple_widget.labeled_combobox(label='Nodetype', parent_layout=vertical_layout, items=nodetype_keys)
        
        
        vertical_layout.addStretch()
        search_button = QtGui.QPushButton('Search')
        search_button.clicked.connect(self.search_clicked)
        vertical_layout.addWidget(search_button)
    
    def search_clicked(self):
        
        pattern = self.regex_lineedit.text()
        set_name = self.set_name_lineedit.text()
        use_parent = self.use_parent_checkbox.isChecked()
        use_longname = self.use_longname_checkbox.isChecked()
        nodetype = self.nodetype_dict.get(self.nodetype_combobox.currentText())
        
        if len(pattern) < 1:
            pm.warning('No regex')
            return
        
        if len(set_name) < 1:
            pm.warning('No set_name')
            return
        
        print(pattern, set_name, use_parent, use_longname, nodetype)
        
        
        
        
        pet_search.create_set_from_regex(   pattern=pattern,
                                            nodetype=nodetype,
                                            use_longname=use_longname,
                                            use_parent=use_parent,
                                            set_name=set_name)

def show():
    win = RegexWidget(parent=maya_main_window())
    win.show()


'''
try:
    win.close()
    
except NameError:
    print('No win to close')
    
win = RegexWidget(parent=maya_main_window())
win.show()
win.move(100,150)
'''