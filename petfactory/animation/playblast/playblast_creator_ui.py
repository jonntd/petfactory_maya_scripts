from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import pprint

import petfactory.gui.simple_widget as simple_widget

import petfactory.util.verify as pet_verify

import petfactory.animation.playblast.playblast_creator as playblast_creator
reload(playblast_creator)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
class MyDelegate(QtGui.QItemDelegate):
    
    def __init__(self, parent=None):
        super(MyDelegate, self).__init__(parent)
        
    def createEditor(self, parent, option, index):
        
        column = index.column()
        
        if column == 2 or column == 3: 
            spinbox = QtGui.QSpinBox(parent)
            spinbox.setRange(-9999,9999)
            spinbox.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            return spinbox
        
        else:
            return QtGui.QLineEdit(parent)
          
class PlayblastWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(PlayblastWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(485, 300)
        self.setWindowTitle('Playblast')
        
        # main layout
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)
        
        # menu bar
        self.menu_bar = QtGui.QMenuBar()
        self.main_layout.addWidget(self.menu_bar)
        
        # add menu
        self.file_menu = self.menu_bar.addMenu('File')
        
        # add sub menus
        self.save_clips_action = QtGui.QAction('Save clips', self)
        self.save_clips_action.triggered.connect(self.save_clips_action_triggered)
        self.file_menu.addAction(self.save_clips_action)
        
        self.load_clips_action = QtGui.QAction('Load clips', self)
        self.load_clips_action.triggered.connect(self.load_clips_action_triggered)
        self.file_menu.addAction(self.load_clips_action)
        
        # content layout
        self.content_layout = QtGui.QVBoxLayout()
        self.content_layout.setContentsMargins(7,7,7,7)
        self.main_layout.addLayout(self.content_layout)
        
        
        # -----------------------------------------------------------------------
        
        # model
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Camera', 'Suffix', 'start', 'end'])
        
        
        # tableview
        self.clip_tableview = QtGui.QTableView()
        self.clip_tableview.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.clip_tableview.setAlternatingRowColors(True)
        self.clip_tableview.setModel(self.model)
        self.clip_tableview.setItemDelegate(MyDelegate(self.clip_tableview))
        #h_header = self.clip_tableview.horizontalHeader()
        #h_header.setResizeMode(QtGui.QHeaderView.Stretch)
        
        self.clip_tableview.setColumnWidth(0, 200)
        self.clip_tableview.setColumnWidth(1, 100)
        self.clip_tableview.setColumnWidth(2, 75)
        self.clip_tableview.setColumnWidth(3, 75)
        
        self.content_layout.addWidget(self.clip_tableview)
        
        
        
        
        # add joint ref
        add_remove_cam_hbox = QtGui.QHBoxLayout()
        self.content_layout.addLayout(add_remove_cam_hbox)  
        
        # add
        add_cam_button = QtGui.QPushButton(' + ')
        add_cam_button.setMinimumWidth(40)
        
        add_remove_cam_hbox.addWidget(add_cam_button)
        add_cam_button.clicked.connect(self.add_cam_button_click)
        
        # remove
        remove_cam_button = QtGui.QPushButton(' - ')
        remove_cam_button.setMinimumWidth(40)
        
        add_remove_cam_hbox.addWidget(remove_cam_button)
        remove_cam_button.clicked.connect(self.remove_cam_button_click)
        
        add_remove_cam_hbox.addStretch()
        
        self.resolution_dict = {'1920 x 1080':(1920, 1080),
                                '1280 x 720':(1280, 720),
                                '960 x 540':(960, 540)}
                                
        resolution_keys = self.resolution_dict.keys()
        resolution_keys.sort()
        
        # resolution
        self.resolution_combobox = simple_widget.labeled_combobox(label='Resolution', parent_layout=self.content_layout, items=resolution_keys)
        
        
        # do it
        playblast_hbox = QtGui.QHBoxLayout()
        self.content_layout.addLayout(playblast_hbox)
        
        playblast_button = QtGui.QPushButton('Playblast')
        playblast_button.setMinimumWidth(125)
        playblast_hbox.addStretch()
        playblast_hbox.addWidget(playblast_button)
        playblast_button.clicked.connect(self.playblast_clicked)
        
        
    # stop keypress event propagation
    def keyPressEvent(self, event):
        pass
        #if event.key() == QtCore.Qt.Key_Escape:
            #print('ESCAPE')
            
    def playblast_clicked(self):
        
        width, height = self.resolution_dict.get(self.resolution_combobox.currentText())
        
        
        # get the camera info form the table view
        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
        
        if num_children < 1:
            pm.warning('Please add some cameras to the tableview!')
            return
        
        clip_list = []
        
        playblast_dict = {}
        playblast_dict['width'] = width
        playblast_dict['height'] = height
        playblast_dict['clips'] = clip_list
        
        
        
        for i in range(num_children):
            
            info_dict = {}
            clip_list.append(info_dict)
            
            child = root.child(i)
            
            if child.checkState():
                
                cam_name = child.text()
                
                if pet_verify.verify_string(cam_name, pm.nodetypes.Camera):
                    
                    row = child.row()
                    
                    camera = pet_verify.to_pynode(cam_name)
                    
                    if camera is None:
                        pm.warning('Not a valid camera, skipping')
                        continue
                        
                    start_time = self.model.item(row, 2)
                    
                    if start_time is None:
                        pm.warning('No start time specified, skipping')
                        continue
                        
                    end_time = self.model.item(row, 3)
                    
                    if end_time is None:
                        pm.warning('No end time specified, skipping')
                        continue
                        
                    
                    info_dict['camera'] = camera
                    info_dict['start_time'] = start_time.text()
                    info_dict['end_time'] = end_time.text()
                    
                    

                    
                    
        pprint.pprint(playblast_dict)
        
        
        '''
        do_playblast(   current_camera,
                        start_time,
                        end_time,
                        file_name,
                        width,
                        height)
        '''
        
    def add_cam_button_click(self):
        
        sel_list = pm.ls(sl=True)
        
        
        for sel in sel_list:
            if pet_verify.verify_pynode(sel, pm.nodetypes.Camera):
                
                win.add_clip(pet_verify.to_transform(sel).shortName())
    
    def remove_cam_button_click(self):
        
        selection_model = self.clip_tableview.selectionModel()
        
        # returns QModelIndex
        selected_rows = selection_model.selectedRows()
        
        row_list = [sel.row() for sel in selected_rows]
        row_list.sort(reverse=True)
        
        for row in row_list:
            self.model.removeRow(row)
            
            
    def add_clip(self, name):
        
        item = QtGui.QStandardItem()
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.Checked)
        
        item.setData(name, QtCore.Qt.EditRole)
                
        self.model.appendRow(item) 
    
    def save_clips_action_triggered(self):
        print(self.sender())
        
    
    def load_clips_action_triggered(self):
        print(self.sender())


def show():
    win = PlayblastWidget(parent=maya_main_window())
    win.show()

try:
    win.close()
    
except NameError:
    pass 
    
win = PlayblastWidget(parent=maya_main_window())
win.show()
win.move(100,150)
