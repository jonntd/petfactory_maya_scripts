from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial
import pprint
import maya.mel as mel
import os
import json
import pymel.core as pm

import petfactory.gui.simple_widget as simple_widget

import petfactory.util.verify as pet_verify

import petfactory.animation.playblast.playblast_creator as playblast_creator
reload(playblast_creator)

import petfactory.gui.persistence as pet_persistence
reload(pet_persistence)

import petfactory.animation.playblast.camera_sequenser as camera_sequenser
reload(camera_sequenser)

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
        
        self.output_dir = None
        
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
        
        self.set_output_dir_action = QtGui.QAction('Set output directory', self)
        self.set_output_dir_action.triggered.connect(self.set_output_dir_triggered)
        self.file_menu.addAction(self.set_output_dir_action)
        
        
        # content layout
        self.content_layout = QtGui.QVBoxLayout()
        self.content_layout.setContentsMargins(7,7,7,7)
        self.main_layout.addLayout(self.content_layout)
        
        
        # -----------------------------------------------------------------------
        #
        # clips
        #
        # -----------------------------------------------------------------------
        
        # clip group box
        clip_groupbox = QtGui.QGroupBox("Clips")
        self.content_layout.addWidget(clip_groupbox)
        clip_groupbox_vbox = QtGui.QVBoxLayout()
        clip_groupbox.setLayout(clip_groupbox_vbox)
        
        
        # model
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Camera', 'Notes', 'start', 'end'])  
        
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
        

        
        # -----------------------------------------------------------------------
        #
        # Camera
        #
        # -----------------------------------------------------------------------
        
        
        # camera group box
        camera_groupbox = QtGui.QGroupBox("Camera")
        self.content_layout.addWidget(camera_groupbox)

        # grid layout
        camera_groupbox_gridlayout = QtGui.QGridLayout()
        camera_groupbox.setLayout(camera_groupbox_gridlayout)
        camera_groupbox_gridlayout.setColumnStretch(3, 1)
        camera_groupbox_gridlayout.setColumnMinimumWidth(0, 100)
        camera_groupbox_gridlayout.setColumnMinimumWidth(1, 150)
        
        # start end time label
        start_end_time_label = QtGui.QLabel('Set start/end time')
        camera_groupbox_gridlayout.addWidget(start_end_time_label, 0, 0)
        
        # start end time button layout
        set_start_end_time_hbox = QtGui.QHBoxLayout()
        camera_groupbox_gridlayout.addLayout(set_start_end_time_hbox, 0, 1)
        
        # set start time
        self.set_start_time_button = QtGui.QPushButton('|<')
        self.set_start_time_button.setFixedWidth(40)
        set_start_end_time_hbox.addWidget(self.set_start_time_button)
        self.set_start_time_button.clicked.connect(self.set_time_button_clicked)
        
        #set_start_end_time_hbox.addStretch()
        # set to range
        set_to_range_button = QtGui.QPushButton('Use Range')
        set_start_end_time_hbox.addWidget(set_to_range_button, 1, 1)
        set_to_range_button.clicked.connect(self.set_to_range_clicked)
        
        
        # set start time
        self.set_end_time_button = QtGui.QPushButton('>|')
        self.set_end_time_button.setFixedWidth(40)
        set_start_end_time_hbox.addWidget(self.set_end_time_button)
        self.set_end_time_button.clicked.connect(self.set_time_button_clicked)
        

        # look through camera
        look_through_button = QtGui.QPushButton('Look through camera')
        camera_groupbox_gridlayout.addWidget(look_through_button, 1, 1)
        look_through_button.clicked.connect(self.look_through_button_click)
        
        # set to range
        set_to_range_button = QtGui.QPushButton('Selsect camera')
        camera_groupbox_gridlayout.addWidget(set_to_range_button, 2, 1)
        set_to_range_button.clicked.connect(self.select_camera)
        
        
        

        
        # -----------------------------------------------------------------------
        #
        # Output
        #
        # -----------------------------------------------------------------------
        
        
        # camera group box
        output_groupbox = QtGui.QGroupBox("Output")
        self.content_layout.addWidget(output_groupbox)
        output_groupbox_vbox = QtGui.QVBoxLayout()
        output_groupbox.setLayout(output_groupbox_vbox)
        
        
        
        # resolution
        self.resolution_dict = {'1920 x 1080':(1920, 1080),
                                '1280 x 720':(1280, 720),
                                '960 x 540':(960, 540)}
                                
        resolution_keys = self.resolution_dict.keys()
        resolution_keys.sort()
        
        self.resolution_combobox = simple_widget.labeled_combobox(label='Resolution', parent_layout=output_groupbox_vbox, items=resolution_keys)
        
        
        # do playblast
        playblast_hbox = QtGui.QHBoxLayout()
        self.content_layout.addLayout(playblast_hbox)
        
        playblast_button = QtGui.QPushButton('Playblast')
        playblast_button.setMinimumWidth(125)
        playblast_hbox.addStretch()
        playblast_hbox.addWidget(playblast_button)
        playblast_button.clicked.connect(self.playblast_clicked)
        
        
        # do camera sequenser
        sequenser_hbox = QtGui.QHBoxLayout()
        self.content_layout.addLayout(sequenser_hbox)
        
        sequenser_button = QtGui.QPushButton('Sequenser')
        sequenser_button.setMinimumWidth(125)
        sequenser_hbox.addStretch()
        sequenser_hbox.addWidget(sequenser_button)
        sequenser_button.clicked.connect(self.sequenser_clicked)
        
        
    # stop keypress event propagation
    def keyPressEvent(self, event):
        pass
        #if event.key() == QtCore.Qt.Key_Escape:
            #print('ESCAPE')
    
    def set_to_range_clicked(self):
        print(self.sender())
        
    def sequenser_clicked(self):
        
        info_dict = self.build_info_dict() 
                            
        if info_dict is None:
            return
            
            
        clip_info_list = info_dict.get('clips')
        width = info_dict.get('width')
        height = info_dict.get('height')
        
        current_shot = None
        for clip_info in clip_info_list:
            
            checked = clip_info.get('checked')
            
            if not checked:
                print('Clip is unchecked, skipping...')
                continue
            
            start_time = clip_info.get('start_time')
            end_time = clip_info.get('end_time') 
            
            if start_time > end_time:
                print('Start time is greater than end time, skipping...')
                continue
                
            
            cam = clip_info.get('camera')
            
            if not pet_verify.verify_string(cam, pm.nodetypes.Camera):
                print('Not a valid camera, skipping...')
                continue
                
            
            #notes = clip_info.get('notes')         
            cam_node = pet_verify.to_pynode(cam)
            
            print(cam_node, start_time, end_time)
            
            
            shot = camera_sequenser.create_shot(camera=cam_node, start_time=start_time, end_time=end_time, current_shot=current_shot)
            current_shot = shot

        
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
        
        num_children = self.model.rowCount()
        
        if num_children < 1:
            pm.warning('Please add some cameras to the tableview!')
            return None
        
        clip_list = []
        playblast_dict = {}
        playblast_dict['clips'] = clip_list

        
        for row in range(num_children):

            camera_item = self.model.item(row, 0)
            camera_name = camera_item.text()
            camera_node = pet_verify.to_pynode(camera_name)
                        
            start_time_item = self.model.item(row, 2)    
            end_time_item = self.model.item(row, 3)
            
            start_time_text = start_time_item.text()
            end_time_text = end_time_item.text()
        
            notes_item = self.model.item(row, 1)

            # add the dict
            info_dict = {}
            clip_list.append(info_dict)
            
            info_dict['camera'] = camera_node.shortName()
            info_dict['start_time'] = int(start_time_text)
            info_dict['end_time'] = int(end_time_text)
            info_dict['notes'] = notes_item.text()
            info_dict['checked'] = True if camera_item.checkState() else False
                
                
        width, height = self.resolution_dict.get(self.resolution_combobox.currentText())
        playblast_dict['width'] = width
        playblast_dict['height'] = height
        
        return playblast_dict
                
        
        
    def playblast_clicked(self):
        
        if self.output_dir is None:
            pm.warning('Output directory not set! File > Set output directory')
            return
            
        if not os.path.exists(self.output_dir):
            pm.warning('{0} is not a valid directory! Please set a new one'.format(self.output_dir))
            self.output_dir = None
            return
        
     
        info_dict = self.build_info_dict() 
        
        dir_path = playblast_creator.create_playblast_directory(self.output_dir)
        
        if dir_path is None:
            return
            
        if info_dict is None:
            return
            
            
        clip_info_list = info_dict.get('clips')
        width = info_dict.get('width')
        height = info_dict.get('height')
            
        for clip_info in clip_info_list:
            
            checked = clip_info.get('checked')
            
            if not checked:
                print('Clip is unchecked, skipping...')
                continue
            
            start_time = clip_info.get('start_time')
            end_time = clip_info.get('end_time') 
            
            if start_time > end_time:
                print('Start time is greater than end time, skipping...')
                continue
                
            
            cam = clip_info.get('camera')
            
            if not pet_verify.verify_string(cam, pm.nodetypes.Camera):
                print('Not a valid camera, skipping...')
                continue
                
            

            notes = clip_info.get('notes')         
            cam_node = pet_verify.to_pynode(cam)            
                
            playblast_creator.do_playblast( current_camera=cam_node,
                                            file_name='{0}_{1}'.format(cam, notes),
                                            start_time=start_time,
                                            end_time=end_time,
                                            dir_path=dir_path,
                                            width=width,
                                            height=height)
                                            
                                            
                                           
        # save json
        json_data = json.dumps(info_dict, indent=4)
        json_path = os.path.join(dir_path, 'playblast.json')
        
        with open(json_path, 'w') as f:
            f = open(json_path,'w')
            f.write(json_data)
            f.close()

    
    def look_through_button_click(self):
        
        current_row = self.get_selected_row()
        
        if current_row is None:
            return
        
        camera_string = self.model.item(current_row, 0).text() 
        current_camera = pet_verify.to_pynode(camera_string)
        
        
        if current_camera is None:
            pm.warning('The camera "{0}" does not exist'.format(camera_string))
            return
            
        
        start_time = int(self.model.item(current_row, 2).text())
        end_time = int(self.model.item(current_row, 3).text())

        mel.eval('lookThroughModelPanel {0} modelPanel4'.format(current_camera))
        
        
        if start_time > end_time:
            pm.warning('The start time cannot be greater than the end time!')
            
        else:
            pm.playbackOptions(min=start_time, max=end_time)
   
   
    def select_camera(self):
        
        current_row = self.get_selected_row()
        
        if current_row is None:
            return
        
        camera_string = self.model.item(current_row, 0).text() 
        current_camera = pet_verify.to_pynode(camera_string)
        
        
        if current_camera is None:
            pm.warning('The camera "{0}" does not exist'.format(camera_string))
            return
            
        pm.select(current_camera)

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
                    first_keyframe = last_keyframe = '0'
                
                self.add_clip(pet_verify.to_transform(sel).shortName(), first_keyframe, last_keyframe, '', True)
            else:
                pm.warning('Make sure you have a camera selected!')
    
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
            
            
    def add_clip(self, name, start_time, end_time, notes, checked):
        
        #print(name, start_time, end_time, notes)

        # cam item
        cam_item = QtGui.QStandardItem(name)
        cam_item.setCheckable(True)
        
        
        if checked:
            cam_item.setCheckState(QtCore.Qt.Checked)  
        else:
            cam_item.setCheckState(QtCore.Qt.Unchecked)
            
        # add other items
        start_time_item = QtGui.QStandardItem(str(int(start_time)))
        notes_item = QtGui.QStandardItem(notes)
        end_time_item = QtGui.QStandardItem(str(int(end_time)))
        
        # add itemns to model
        # get the curr num rows so that we can insert the items at a free row
        num_rows = self.model.rowCount()
        
        self.model.setItem(num_rows, 0, cam_item)
        self.model.setItem(num_rows, 1, notes_item)
        self.model.setItem(num_rows, 2, start_time_item)
        self.model.setItem(num_rows, 3, end_time_item)
        
   
  
    def save_clips_action_triggered(self):
        
        playblast_dict = self.build_info_dict()
        
        if playblast_dict is None:
            return
        
        #pprint.pprint(playblast_dict)
        
        clip_list = playblast_dict.get('clips')
        if len(clip_list) < 1:
            pm.warning('The clip list is empty, file not saved.')
            return None
  
        pet_persistence.save_json(playblast_dict, title='Save clips', filter='JSON (*.json)')

    def set_output_dir_triggered(self):
        
        start_dir = pm.workspace.getPath()
        self.output_dir = pet_persistence.select_dir(title='Select output dir', dir=start_dir)
               
        
    def load_clips_action_triggered(self):
     
        info_dict = pet_persistence.load_json(title='Load clips', filter='JSON (*.json)')
        #pprint.pprint(info_dict)
        
        if info_dict is None:
            return
        
        cam_info_list = info_dict.get('clips')
        
        if cam_info_list is None:
            pm.warning('Could not load clips!')
            return
                
        for cam_info in cam_info_list:
            
            cam = cam_info.get('camera')
            start_time = cam_info.get('start_time')
            end_time = cam_info.get('end_time')
            notes = cam_info.get('notes')
            checked = cam_info.get('checked')
                        
            self.add_clip(name=cam, start_time=start_time, end_time=end_time, notes=notes, checked=checked)


def show():
    win = PlayblastWidget(parent=maya_main_window())
    win.show()
    return win

'''
try:
    win.close()
    
except NameError:
    pass 
    
win = show()
win.move(150,150)

win.add_clip(name='camera1', start_time=10, end_time=30, notes='a 1 string', checked=False)
win.add_clip(name='camera2', start_time=20, end_time=40, notes='a 2 string', checked=True)
'''