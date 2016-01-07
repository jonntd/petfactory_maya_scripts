from PySide import QtCore, QtGui
import sys, os
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)
'''
def get_attr_dict(canvas_node, allowed_attr):
    
    user_defined_attr = canvas_node.listAttr(userDefined=True, settable=True)               
    attr_dict = {}
    
    for attr in user_defined_attr:
                
        try:

            # Check if the plug is a child plug.
            # A child plugs parent is always a compound plug.
            if attr.isChild():
                continue

            index = allowed_attr.index(attr.type())

            attr_dict[attr.name(includeNode=False)] = attr.get()
            
        except ValueError:
            pass
            
    return attr_dict


def set_attr_dict(canvas_node_list, attr_dict):
    
    for canvas_node in canvas_node_list:
        
        for attr, value in attr_dict.iteritems():
            
            try:
                pm.setAttr('{}.{}'.format(canvas_node, attr), value)
                
            except pm.MayaAttributeError as e:
                print('could not set attr. {}'.format(e))
 
    
def copy_canvas_attr(canvas_source, canvas_targets):
    
    valid_attr_type = ['bool', 'double', 'long']
    attr_dict = get_attr_dict(canvas_source, valid_attr_type)
    set_attr_dict(canvas_targets, attr_dict)


def copy_from_sel():

    sel_list = pm.ls(sl=True)

    if len(sel_list) < 2:
        pm.warning('Please select 2 canvas nodes!')
        return
    
    if isinstance(sel_list[0], pm.nodetypes.CanvasNode):
        source = sel_list[0]
    else:
        pm.warning('Make sure that selected nodes are canvasNodes!')
        return

    targets = []

    for sel in sel_list[1:]:
        if isinstance(sel_list[0], pm.nodetypes.CanvasNode):
            targets.append(sel)

    if len(targets) > 0:
        copy_canvas_attr(source, targets)
        #print(source)
        #print(targets)

    else:
        pm.warning('Make sure that selected nodes are canvasNodes!')
'''

def connect_selected_crv(crv_xfo, canvas_node, profile, profile_count):
    
    try:
        crv_shape = crv_xfo.getShape()
        crv_cvs = crv_shape.getCVs()
    
    except AttributeError as e:
        pm.warning('{}'.format(e))
        return
        
    
    try:
        pm.setAttr('{}.{}'.format(canvas_node, profile_count), len(crv_cvs))
        
        profile_attr = pm.general.Attribute('{}.{}'.format(canvas_node, profile))
        for index, cv in enumerate(crv_cvs):

            #crv_shape.controlPoints[index] >> canvas_node.sideProfile[index]
            crv_shape.controlPoints[index] >> profile_attr[index]
            
    except AttributeError as e:
        pm.warning('{}'.format(e))
        
        

def remove_input_crv(canvas_node, profile, profile_count):
    
    try:
        #num = canvas_node.sideProfile.numElements()
        profile_attr = pm.general.Attribute('{}.{}'.format(canvas_node, profile))
        num = profile_attr.numElements()
    
        profile_attr = pm.general.Attribute('{}.{}'.format(canvas_node, profile))
        for i in range(num):

            if profile_attr[i].isConnected():
               profile_attr[i].disconnect()

            #if canvas_node.sideProfile[i].isConnected():
               #canvas_node.sideProfile[i].disconnect()
               
        #canvas_node.sideProfileCount.set(0)
        pm.setAttr('{}.{}'.format(canvas_node, profile_count), 0)
        
    except AttributeError as e:
        pm.warning('{}'.format(e))
    
    
    
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
       
class Panel(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(Panel, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setGeometry(200, 200, 250, 100)
        self.setWindowTitle('TwoCircleTangent')
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self.profileAttrList = [['sideProfile', 'sideProfileCount'],
                                ['cap1Profile', 'cap1ProfileCount'],
                                ['cap2Profile', 'cap2ProfileCount']]
        
        # create canvas node
        create_canvas_node_btn = QtGui.QPushButton('Create canvas node')
        vbox.addWidget(create_canvas_node_btn)
        create_canvas_node_btn.clicked.connect(self.create_canvas_node_btn_clicked)
        
        
        # canvas node lineedit
        self.canvas_lineedit = simple_widget.add_filtered_populate_lineedit(label='  canvasNode >> ', parent_layout=vbox, nodetype=pm.nodetypes.CanvasNode)

        self.profile_combobox = QtGui.QComboBox()
        vbox.addWidget(self.profile_combobox)
        self.profile_combobox.addItems(['Side', 'Cap 1', 'Cap 2'])


        # connect        
        connect_cvs_btn = QtGui.QPushButton('Connect CVs to profile')
        vbox.addWidget(connect_cvs_btn)
        connect_cvs_btn.clicked.connect(self.connect_cvs_btn_clicked)
        
        p = connect_cvs_btn.palette()
        p.setColor(connect_cvs_btn.backgroundRole(), QtGui.QColor(0,100,0))
        connect_cvs_btn.setPalette(p)

        # break connections        
        break_con_btn = QtGui.QPushButton('Break connection')
        vbox.addWidget(break_con_btn)
        break_con_btn.clicked.connect(self.break_con_btn_clicked)
        
        p = break_con_btn.palette()
        p.setColor(break_con_btn.backgroundRole(), QtGui.QColor(100,0,0))
        break_con_btn.setPalette(p)

        '''
        # copy attr        
        copy_attr_btn = QtGui.QPushButton('Copy attr')
        vbox.addWidget(copy_attr_btn)
        copy_attr_btn.clicked.connect(self.copy_attr_btn_clicked)
        '''

        vbox.addStretch()
        
    #def copy_attr_btn_clicked(self):
        #copy_from_sel()

    def create_canvas_node_btn_clicked(self):
        
        canvasNode = pm.createNode('canvasNode')
        path = '/Users/johan/Dev/fabricEngine/canvas/polygon/twoCircleTangent/twoCircleTangentXfoFlip.canvas'
        pm.dfgImportJSON(m=canvasNode, f=path)
        self.canvas_lineedit.setText(canvasNode.name())

        loc = pm.createNode('locator')
        canvasNode.dummy >> loc.v
        
    def break_con_btn_clicked(self):
        
        index = self.profile_combobox.currentIndex()
        profile = self.profileAttrList[index][0]
        profileCount = self.profileAttrList[index][1]

        print(profile, profileCount)

        canvas_node = pm.PyNode(self.canvas_lineedit.text())
        remove_input_crv(canvas_node, profile, profileCount)

        
    def connect_cvs_btn_clicked(self):
        
        index = self.profile_combobox.currentIndex()
        profile = self.profileAttrList[index][0]
        profileCount = self.profileAttrList[index][1]

        print(profile, profileCount)

        canvas_node = pm.PyNode(self.canvas_lineedit.text())
        crv_xfo = pm.ls(sl=True)[0]
        connect_selected_crv(crv_xfo, canvas_node, profile, profileCount)

def show():
    win = Panel(parent=maya_main_window())
    win.show()
    return win

#show()