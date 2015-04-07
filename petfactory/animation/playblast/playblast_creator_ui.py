from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import pprint
import maya.mel as mel
import os
import json

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
        
        # clip group box
        clip_groupbox = QtGui.QGroupBox("Clips")
        self.content_layout.addWidget(clip_groupbox)
        clip_groupbox_vbox = QtGui.QVBoxLayout()
        clip_groupbox.setLayout(clip_groupbox_vbox)
        
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
        
        clip_groupbox_vbox.addWidget(self.clip_tableview)
        
        
        
        
        # tableview buttons layout
        add_remove_cam_hbox = QtGui.QHBoxLayout()
        clip_groupbox_vbox.addLayout(add_remove_cam_hbox)  
        
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
        
        # set start time
        self.set_start_time_button = QtGui.QPushButton('|<')
        add_remove_cam_hbox.addWidget(self.set_start_time_button)
        self.set_start_time_button.clicked.connect(self.set_time_button_clicked)
        
        # set start time
        self.set_end_time_button = QtGui.QPushButton('>|')
        add_remove_cam_hbox.addWidget(self.set_end_time_button)
        self.set_end_time_button.clicked.connect(self.set_time_button_clicked)
        
        # look through camera
        look_through_button = QtGui.QPushButton('Look through camera')
        add_remove_cam_hbox.addWidget(look_through_button)
        look_through_button.clicked.connect(self.look_through_button_click)
        
        
        
        
        
        
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
    
    def get_selected_row(self):
        
        selection_model = self.clip_tableview.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        
        if len(selected_indexes) < 1:
            pm.warning('No clip is selected!')
            return None
            
        return selected_indexes[0].row()
        
    def set_time_button_clicked(self):

        selected_row = self.get_selected_row()
        
        if selected_row is None:
            return

        if self.sender() == self.set_start_time_button:
            item = self.model.item(selected_row, 2)
            item.setText(str(int(pm.currentTime(q=True))))

        else:
            item = self.model.item(selected_row, 3)
            item.setText(str(int(pm.currentTime(q=True))))
    
    def build_info_dict(self):
        
        # get the camera info form the table view
        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
        
        if num_children < 1:
            pm.warning('Please add some cameras to the tableview!')
            return
        
        clip_list = []
        playblast_dict = {}
        playblast_dict['clips'] = clip_list

        
        for i in range(num_children):

            child = root.child(i)
            
            if child.checkState():
                
                info_dict = {}
                clip_list.append(info_dict)

                row = child.row()
                
                cam_name = child.text()
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
                    
                
                info_dict['camera'] = camera.shortName()
                info_dict['start_time'] = start_time.text()
                info_dict['end_time'] = end_time.text()
                
                
        width, height = self.resolution_dict.get(self.resolution_combobox.currentText())
        playblast_dict['width'] = width
        playblast_dict['height'] = height
        
        return playblast_dict
                
        
        
    def playblast_clicked(self):
        
        playblast_dict = self.build_info_dict()         
        #pprint.pprint(playblast_dict)
        
        clip_info_list = playblast_dict.get('clips')
        width = playblast_dict.get('width')
        height = playblast_dict.get('height')
        
        dir_path = playblast_creator.create_playblast_directory()
        
        if dir_path is None:
            return
    
        for clip_info in clip_info_list:
            
            cam = clip_info.get('camera')
            start_time = clip_info.get('start_time')
            end_time = clip_info.get('end_time')
            
            cam_node = pet_verify.to_pynode(cam)
            
                
            playblast_creator.do_playblast( current_camera=cam_node,
                                            file_name='{0}_clip'.format(cam),
                                            start_time=start_time,
                                            end_time=end_time,
                                            dir_path=dir_path,
                                            width=width,
                                            height=height)
    
    def look_through_button_click(self):
        
        current_row = self.get_selected_row()
        
        if current_row is None:
            return
        
        camera_string = self.model.item(current_row, 0).text() 
        current_camera = pet_verify.to_pynode(camera_string)
        
        
        if current_camera is None:
            pm.warning('The camera "{0}" does not exist'.format(camera_string))
            return
            
        
        start_time = self.model.item(current_row, 2).text()
        end_time = self.model.item(current_row, 3).text() 

        mel.eval('lookThroughModelPanel {0} modelPanel4'.format(current_camera))
        
        
        if start_time > end_time:
            pm.warning('The start time cannot be greater than the end time!')
            
        else:
            pm.playbackOptions(min=start_time, max=end_time)
   

    def add_cam_button_click(self):
        
        sel_list = pm.ls(sl=True)
        sel_list.sort()
        
        
        for sel in sel_list:
            
            if pet_verify.verify_pynode(sel, pm.nodetypes.Camera):
                
                # get keyframes info from the camera
                key_list = list(set(pm.keyframe(sel, q=True, timeChange=True)))
                
                if len(key_list) > 0:
                    key_list.sort()
                    first_keyframe = key_list[0]
                    last_keyframe = key_list[-1]
                    
                else:
                    first_keyframe = last_keyframe = 0
                
                win.add_clip(pet_verify.to_transform(sel).shortName(), first_keyframe, last_keyframe)
    
    def remove_cam_button_click(self):
        
        selection_model = self.clip_tableview.selectionModel()
        
        # returns QModelIndex
        selected_rows = selection_model.selectedRows()
        
        if len(selected_rows) < 1:
            pm.warning('Select an entire row to delete a track!')
            return
        
        row_list = [sel.row() for sel in selected_rows]
        row_list.sort(reverse=True)
        
        for row in row_list:
            self.model.removeRow(row)
            
            
    def add_clip(self, name, start_time, end_time):
        
        num_rows = self.model.rowCount()
   
        # cam item
        cam_item = QtGui.QStandardItem()
        cam_item.setCheckable(True)
        cam_item.setData(name, QtCore.Qt.EditRole)
        
        # uncheck cameras that have no animation
        if start_time == end_time:
            cam_item.setCheckState(QtCore.Qt.Unchecked)
            
        else:
            cam_item.setCheckState(QtCore.Qt.Checked)

        # start time item
        start_time_item = QtGui.QStandardItem()
        start_time_item.setData(start_time, QtCore.Qt.EditRole)
        
        # end time item
        end_time_item = QtGui.QStandardItem()
        end_time_item.setData(end_time, QtCore.Qt.EditRole) 
                
        self.model.setItem(num_rows, 0, cam_item)
        self.model.setItem(num_rows, 2, start_time_item)
        self.model.setItem(num_rows, 3, end_time_item)
        
        
        #print(start_time, end_time)
        
        

    
    def save_clips_action_triggered(self):
        
        file_name, selected_filter = QtGui.QFileDialog.getSaveFileName(None, 'Save Keyframes', None, 'JSON (*.json)')
    
        playblast_dict = self.build_info_dict() 
        json_data = json.dumps(playblast_dict, indent=4)
        
        if file_name:
            with open(file_name, 'w') as f:
                f = open(file_name,'w')
                f.write(json_data)
                f.close()
                print('Data saved to file: {0}'.format(file_name))       
    
        else:
            print('Could not save file')
        
    
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
win.move(250,150)

