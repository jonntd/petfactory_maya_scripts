import pymel.core as pm
from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pprint
import petfactory.rigging.joint_tools as joint_tools
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics
#reload(nhair_dynamics)

import petfactory.rigging.ctrl.ctrl as pet_ctrl
#reload(pet_ctrl)



# build the joints from the joint ref group
def build_joints(joint_ref_list, name_list=None):
    
    ret_list = []
       
    for index, joint_ref in enumerate(joint_ref_list):
        
        if name_list is not None:
            
            if len(joint_ref_list) != len(name_list):
                pm.warning('The length of name list does not match the ref list! ref name used instead')
                name = joint_ref.nodeName()
                
            else:
                name = name_list[index]
        else:
            name = joint_ref.nodeName()
        
        joint_info = joint_tools.build_joint_info(joint_ref, override_name='{0}'.format(name))
        up_vec = joint_tools.vec_from_transform(joint_ref, 2)
        jnt_list = joint_tools.build_joint_hierarchy(joint_info, up_vec)
        
        ret_list.append({name:jnt_list})  
        
    return ret_list
    



def add_pocedural_wave_anim(info_dict, ctrl_size=1):
    
    #pprint.pprint(info_dict)
    
    root_ctrl = info_dict.get('root_ctrl')
    jnt_list = info_dict.get('joint_list')
    name = info_dict.get('name')
    num_jnt = len(jnt_list)
    
    bind_jnt_list = []
    
    if root_ctrl is None:
        return

    
    # add visibility enum attr to root ctrl
    pm.addAttr(root_ctrl, longName='show_proc_anim_ctrl', at="enum", en="off:on", keyable=True)


    anim_ctrl = pet_ctrl.CreateCtrl.create_circle(name='{0}_sine_anim_ctrl'.format(name), size=ctrl_size)
    
    # lock and hide transformation attrs
    trans_attr = 'tx ty tz rx ry rz sx sy sz'.split(' ')
    [anim_ctrl.setAttr(attr, l=True, k=False) for attr in trans_attr]
    
    root_ctrl.show_proc_anim_ctrl >> anim_ctrl.v
    anim_ctrl.v.set(l=True, k=False)

    pm.parent(anim_ctrl, root_ctrl)
    anim_ctrl.setMatrix(root_ctrl.getMatrix(ws=False))



    # create bind jnt group
    main_bind_jnt_grp = pm.group(em=True, name='{0}_main_bind_jnt_grp'.format(name))
    main_bind_jnt_grp.setMatrix(jnt_list[0].getMatrix())
    pm.parent(main_bind_jnt_grp, root_ctrl)
    
    
    
    # add attr


    
    pm.addAttr(anim_ctrl, longName='sineY', keyable=True)
    pm.addAttr(anim_ctrl, longName='sine_y_global_scale', keyable=True)
    
    pm.addAttr(anim_ctrl, longName='sineZ', keyable=True)
    pm.addAttr(anim_ctrl, longName='sine_z_global_scale', keyable=True)
    
    pm.addAttr(anim_ctrl, longName='time', keyable=True)
     

    for index in range(num_jnt):
        pm.addAttr(anim_ctrl, longName='sine_y_offset{0}'.format(index), keyable=True, defaultValue=index*10)
    
    
    for index in range(num_jnt):
        pm.addAttr(anim_ctrl, longName='sine_y_scale{0}'.format(index), keyable=True, defaultValue=index)
        
    
    for index in range(num_jnt):
        pm.addAttr(anim_ctrl, longName='sine_z_offset{0}'.format(index), keyable=True, defaultValue=index*10)
    
    
    for index in range(num_jnt):
        pm.addAttr(anim_ctrl, longName='sine_z_scale{0}'.format(index), keyable=True, defaultValue=index)
        
       
    # set up nodes
    for index, jnt in enumerate(jnt_list):
        
        
        # create a y sine offset jnt
        sine_y_jnt = pm.createNode('joint', name='sine_y_{0}_jnt'.format(index), ss=True)
        sine_y_jnt.setMatrix(jnt.getMatrix(ws=True))
        pm.parent(sine_y_jnt, jnt)
        
        # create a z sine offset jnt
        sine_z_jnt = pm.createNode('joint', name='sine_z_{0}_jnt'.format(index), ss=True)
        sine_z_jnt.setMatrix(jnt.getMatrix(ws=True))
        pm.parent(sine_z_jnt, sine_y_jnt)
        
       
        # create the bind joints
        bind_jnt = pm.createNode('joint', name='bind_{0}_jnt'.format(index), ss=True)
        bind_jnt_list.append(bind_jnt)
        bind_jnt.setMatrix(jnt.getMatrix(ws=True))
        bind_jnt_grp = pm.group(em=True, name='bind_jnt_{0}_grp'.format(index))
        pm.parentConstraint(sine_z_jnt, bind_jnt_grp)
        pm.parent(bind_jnt, bind_jnt_grp)
        pm.parent(bind_jnt_grp, main_bind_jnt_grp)
        


        
        
        # setup the y sine animation
        
        # pma to offset the vary time input
        pma_sine_y = pm.createNode('plusMinusAverage', name='pma_sine_y{0}'.format(index))
        
        # connect root ctrl time attr to pma
        anim_ctrl.time >> pma_sine_y.input1D[0]
        
        # connect the per joint offset to the pma
        pm.connectAttr('{0}.sine_y_offset{1}'.format(anim_ctrl.longName(), index),  pma_sine_y.input1D[1])
            
        # create node cache
        cache_sine_y = pm.createNode('frameCache', name='frameCache_sine_y{0}_jnt'.format(index))
        
        # connect the pma offsetted time to varytime ant the attr to use as stream to the stream
        pma_sine_y.output1D >> cache_sine_y.varyTime
        anim_ctrl.sineY >> cache_sine_y.stream
        
        # create a per joint scale to the sine
        sine_y_scale = pm.createNode('multDoubleLinear', name='sine_y_scale_{0}'.format(index))
        cache_sine_y.varying >> sine_y_scale.input1
        pm.connectAttr('{0}.sine_y_scale{1}'.format(anim_ctrl.longName(), index), sine_y_scale.input2)
        
        # hook up the gloabal sacle to affect the per joint scale
        sine_y_global_scale_md = pm.createNode('multDoubleLinear', name='sine_y_global_scale_md_{0}'.format(index))       
        anim_ctrl.sine_y_global_scale >> sine_y_global_scale_md.input1
        sine_y_scale.output >> sine_y_global_scale_md.input2
        
        # fianlly feed that into the jnt
        sine_y_global_scale_md.output >> sine_y_jnt.ty
        
        
        
        
        
        # setup the z sine animation
        
        # pma to offset the vary time input
        pma_sine_z = pm.createNode('plusMinusAverage', name='pma_sine_z{0}'.format(index))
        
        # connect root ctrl time attr to pma
        anim_ctrl.time >> pma_sine_z.input1D[0]
        
        # connect the per joint offset to the pma
        pm.connectAttr('{0}.sine_z_offset{1}'.format(anim_ctrl.longName(), index),  pma_sine_z.input1D[1])
            
        # create node cache
        cache_sine_z = pm.createNode('frameCache', name='frameCache_sine_z{0}_jnt'.format(index))
        
        # connect the pma offsetted time to varytime ant the attr to use as stream to the stream
        pma_sine_z.output1D >> cache_sine_z.varyTime
        anim_ctrl.sineZ >> cache_sine_z.stream
        
        # create a per joint scale to the sine
        sine_z_scale = pm.createNode('multDoubleLinear', name='sine_z_scale_{0}'.format(index))
        cache_sine_z.varying >> sine_z_scale.input1
        pm.connectAttr('{0}.sine_z_scale{1}'.format(anim_ctrl.longName(), index), sine_z_scale.input2)
        
        # hook up the gloabal sacle to affect the per joint scale
        sine_z_global_scale_md = pm.createNode('multDoubleLinear', name='sine_z_global_scale_md_{0}'.format(index))       
        anim_ctrl.sine_z_global_scale >> sine_z_global_scale_md.input1
        sine_z_scale.output >> sine_z_global_scale_md.input2
        
        # fianlly feed that into the jnt
        sine_z_global_scale_md.output >> sine_z_jnt.tz
  

    
    # set key frames and handle the post curve behaviour
    
    # setup sine y animation
    pm.setKeyframe(anim_ctrl, v=-1, attribute='sineY', t=0)
    pm.setKeyframe(anim_ctrl, v=1, attribute='sineY', t=48)
    pm.setKeyframe(anim_ctrl, v=-1, attribute='sineY', t=96)
    pm.setInfinity(anim_ctrl, at='sineY', pri='cycleRelative', poi='cycleRelative')
    
    # setup sine z animation
    pm.setKeyframe(anim_ctrl, v=-1, attribute='sineZ', t=0)
    pm.setKeyframe(anim_ctrl, v=1, attribute='sineZ', t=24)
    pm.setKeyframe(anim_ctrl, v=-1, attribute='sineZ', t=48)
    pm.setInfinity(anim_ctrl, at='sineZ', pri='cycleRelative', poi='cycleRelative')
    
    
    # set keyframes of the time attr on the root ctrl, set naim curve properties   
    pm.setKeyframe(anim_ctrl, v=0, attribute='time', t=0)
    pm.setKeyframe(anim_ctrl, v=1, attribute='time', t=1)
    pm.setInfinity(anim_ctrl, at='time', pri='cycleRelative', poi='cycleRelative')
    
    pm.keyTangent(anim_ctrl, edit=True, attribute='time', itt='linear', ott='linear') 
    

    pm.select(deselect=True)
    bind_jnt_set = pm.sets(name='{0}_bind_joints'.format(name))
    bind_jnt_set.addMembers(bind_jnt_list)

  
    
    
def setup_dynamic_joint_chain(jnt_dict, existing_hairsystem=None, ctrl_size=1):
    
    ret_dict = {}
    
    name = jnt_dict.keys()[0]
    jnt_list = jnt_dict.get(name)
    num_jnt = len(jnt_list)
    
    # create groups
    root_main_grp = pm.group(em=True, name='{0}_root_main_grp'.format(name))
    root_ctrl_grp = pm.group(parent=root_main_grp, em=True, name='{0}_root_ctrl_grp'.format(name))
    root_misc_grp = pm.group(parent=root_main_grp, em=True, name='{0}_root_misc_grp'.format(name))
    root_hidden_grp = pm.group(parent=root_misc_grp, em=True, name='{0}_root_hidden_grp'.format(name))
    output_curve_grp = pm.group(parent=root_misc_grp, em=True, name='{0}_output_curve_grp'.format(name))
    
    
    # ctrl
    #root_ctrl = pm.circle(normal=(1,0,0), radius=5, ch=False, name='{0}_root_ctrl'.format(name))[0]
    root_ctrl = pet_ctrl.CreateCtrl.create_circle_arrow(name='{0}_root_ctrl'.format(name), size=ctrl_size)

    
    pm.parent(root_ctrl, root_ctrl_grp)
    root_ctrl_grp.setMatrix(jnt_list[0].getMatrix())

    
    # add attr to ctrl
    pm.addAttr(root_ctrl, longName='display_rig_joints', at="enum", en="off:on", keyable=True)
    
    
    #pm.addAttr(root_ctrl, longName='origBlendshape', minValue=0.0, maxValue=1.0, defaultValue=1.0, keyable=True)
    
    
    pm.addAttr(root_ctrl, longName='dynamic_blendshape', minValue=0.0, maxValue=1.0, defaultValue=0.0, keyable=True)
    pm.addAttr(root_ctrl, longName='stretchScale', minValue=0.0, defaultValue=1.0, keyable=True)
    
    
    
    # cluster group
    cluster_grp = pm.group(parent=root_ctrl, em=True, name='{0}_cluster_grp'.format(name))
    rig_crv_grp = pm.group(parent=root_ctrl, em=True, name='{0}_rig_crv_grp'.format(name))
    
    # jnt group
    jnt_grp = pm.group(em=True, name='{0}_jnt_grp'.format(name))
    
    # position and hide jnt_grp
    root_ctrl.display_rig_joints >> jnt_grp.visibility
    jnt_grp.setMatrix(jnt_list[0].getMatrix())
    
    # parent the jnts and the jnt grp
    pm.parent(jnt_list[0], jnt_grp)
    pm.parent(jnt_grp, root_ctrl)
    
 
    # get the joint positions
    pos_list = [pm.joint(jnt, q=True, p=True, a=True) for jnt in jnt_list]
    
    # build the curve that we will make dynamic, and drive the ik spline rig 
    orig_crv = pm.curve(ep=pos_list, name='orig_curve')


    result_crv = pm.duplicate(orig_crv, name='result_curv')[0]
    orig_crv.worldSpace >> result_crv.create
    # create a curve info node
    result_crv_info = pm.arclen(result_crv, ch=True)
    
     
    num_cvs = orig_crv.getShape().numCVs()

    
    # loop through the cv and add cluster. On cv 0-1 add one cluster,
    # the rest of the cv will have one cluster each, 
    # might add one to the second to last and last
    
    cluster_list = []
    cluster_zero_grp_list = []
    
    for i in range(num_cvs):
            
        clust, clust_handle = pm.cluster('{0}.cv[{1}]'.format(orig_crv.longName(), str(i)), relative=False, name='{0}_{1}_cluster_'.format(name, i))
        cluster_list.append(clust_handle)
        
        # create a group to zero out the transformation
        cluster_zero_grp_list.append(pm.group(em=True, n='ch_zero_grp_{0}'.format(i)))
        
        pm.parent(clust_handle, cluster_zero_grp_list[i])
        
    # parent the cluster zero grp
    pm.parent(cluster_zero_grp_list, cluster_grp)

    
    # make the curves dynamic    
    nhair_dict_list = nhair_dynamics.make_curve_dynamic(orig_crv)
    
    output_curve = nhair_dict_list.get('output_curve')
    follicle = nhair_dict_list.get('follicle')
    nucleus = nhair_dict_list.get('nucleus')
    hairsystem = nhair_dict_list.get('hairsystem')
    
    
    # output curve
    if output_curve:
         
        # blendshape between the cluster driben crv and the dynamic output crv
        result_blendshape = pm.blendShape(output_curve, result_crv, origin='world')[0]
        root_ctrl.dynamic_blendshape >> result_blendshape.weight[0]  

        # create a ik spline
        iks_handle, effector = pm.ikHandle(solver='ikSplineSolver', curve=result_crv, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=jnt_list[0], ee=jnt_list[-1])
        pm.parent(iks_handle, root_hidden_grp)
        ret_dict['output_curve'] = output_curve
        output_curve_shape = output_curve.getShape()
        
        curve_parent = output_curve.getParent()
        pm.parent(output_curve, output_curve_grp)
        pm.delete(curve_parent)
        output_curve.rename('{0}_output_curve'.format(name))
    

    
    else:
        print('could not access the output curve')  
          
      
    # follicle    
    if follicle:
        pm.setAttr('{}.pointLock'.format(follicle.getShape()), 1)
        pm.parent(follicle.getParent(), root_ctrl)
        ret_dict['follicle'] = follicle
        follicle.inheritsTransform.set(False)
        
    else:
        print('could not access the follicle')
      
      
    # nucleus    
    if nucleus:
        nucleus.spaceScale.set(.1)
        ret_dict['nucleus'] = nucleus
        
    else:
        print('could not access the nucleus')
        
        
    
    # hair system  
    if hairsystem:
        
        # if we want to use an existing hair system
        if existing_hairsystem is not None:
            print('Delete current hairsystem, use {0}'.format(existing_hairsystem))
            
            num_connection = len(pm.listConnections('{0}.inputHair'.format(existing_hairsystem)))
            
            follicle.outHair >> existing_hairsystem.inputHair[num_connection]
            existing_hairsystem.outputHair[num_connection] >> follicle.currentPosition
            
            pm.delete(hairsystem)
            
        else:         
            hairsystem.startCurveAttract.set(0.005)
            
        ret_dict['hairsystem'] = hairsystem
        
        
    else:
        print('could not access the hairsystem')
        
    
    
    
    # make curves unselectable, enable drawing ovewrride and set to template
    for c in [orig_crv, output_curve_shape, result_crv, jnt_grp]:
        c.overrideEnabled.set(1)
        c.overrideDisplayType.set(2)

    
    
    pm.parent(result_crv, root_hidden_grp)
    
        
    # hide the hidden group
    root_hidden_grp.visibility.set(0)
 
    # setup the joint stretch
    arc_length = result_crv_info.arcLength.get()
    
    md_global_scale = pm.createNode('multiplyDivide', name='global_scale_compensate')
    md_global_scale.operation.set(2)
    
    result_crv_info.arcLength >> md_global_scale.input1X
    root_ctrl.sx >> md_global_scale.input2X
    
    stretch_scale_mult = pm.createNode('multDoubleLinear', name='stretch_scale_mult')
    md_global_scale.outputX >> stretch_scale_mult.input1
    root_ctrl.stretchScale >> stretch_scale_mult.input2

    

    
    for index, jnt in enumerate(jnt_list):
        
        if index is not 0:
            mult_double = pm.createNode('multDoubleLinear', name='jnt_{0}_stretch_mult'.format(index))
            mult_double.input1.set(jnt.tx.get() / arc_length)
            stretch_scale_mult.output >> mult_double.input2
            mult_double.output >> jnt.tx
            
        
        
    
    ret_dict['root_ctrl'] = root_ctrl
    ret_dict['joint_list'] = jnt_list
    ret_dict['name'] = name
    
    return ret_dict
        
        

# manual setup
'''
pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/tendril_thin_mesh_v03.mb', f=True)

# output curve set 

output_curve_set = pm.sets(name='output_curve_set') 
output_curve_list = []

# single setup
def single_setup():
    node_0 = pm.PyNode('flower_jnt_pos_0')
    joint_ref_list = [node_0]
    name_list = ['tendril_0']
    
    # create the joints
    jnt_dict_list = build_joints(joint_ref_list=joint_ref_list, name_list=name_list)
    
    # create the rig
    dyn_joint_dict_0 = setup_dynamic_joint_chain(jnt_dict=jnt_dict_list[0], ctrl_size=1.2)
    
    # add procedural anim
    if dyn_joint_dict_0:
        add_pocedural_wave_anim(dyn_joint_dict_0)

single_setup()
'''


'''

node_0 = pm.PyNode('flower_jnt_pos_0')
node_1 = pm.PyNode('flower_jnt_pos_1')
node_2 = pm.PyNode('flower_jnt_pos_2')

ref_list = [node_0, node_1, node_2]
jnt_dict_list = build_joints(ref_list, name_list=['tendril_a', 'tendril_b', 'tendril_c'])


dyn_joint_dict_0 = setup_dynamic_joint_chain(jnt_dict_list[0])
hairsystem_0 = dyn_joint_dict_0.get('hairsystem')
output_curve_list.append(dyn_joint_dict_0.get('output_curve'))
add_pocedural_wave_anim(dyn_joint_dict_0)


dyn_joint_dict_1 = setup_dynamic_joint_chain(jnt_dict_list[1], existing_hairsystem=hairsystem_0)
output_curve_list.append(dyn_joint_dict_1.get('output_curve'))
add_pocedural_wave_anim(dyn_joint_dict_1)



output_curve_set.addMembers(output_curve_list)

'''




def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class Import_nuke_2d_track_ui(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(Import_nuke_2d_track_ui, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,100)
        self.setWindowTitle("Tendril Setup")
        
        
        # layout
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        # tendril name
        self.name_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.name_horiz_layout)
        
        self.name_label = QtGui.QLabel('Tendril Name')
        self.name_horiz_layout.addWidget(self.name_label)
        
        self.name_line_edit = QtGui.QLineEdit()
        self.name_horiz_layout.addWidget(self.name_line_edit)
          
        # tree view
        self.model = QtGui.QStandardItemModel()
        
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        #self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
        #self.tree_view.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.tree_view.setAlternatingRowColors(True)
 
        
        self.tree_view.setModel(self.model)
        self.vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['Ref Group', 'Name'])
        
        #header = self.tree_view.header()
        #header.setResizeMode(QtGui.QHeaderView.Stretch)
        #header.setVisible(False)
        
        # add joint ref
        self.joint_ref_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.joint_ref_horiz_layout)        
        
        # add
        self.add_joint_ref_button = QtGui.QPushButton(' + ')
        self.add_joint_ref_button.setMinimumWidth(40)
        
        self.joint_ref_horiz_layout.addWidget(self.add_joint_ref_button)
        self.add_joint_ref_button.clicked.connect(self.add_joint_ref_click)
        
        # remove
        self.remove_joint_ref_button = QtGui.QPushButton(' - ')
        self.remove_joint_ref_button.setMinimumWidth(40)
        
        self.joint_ref_horiz_layout.addWidget(self.remove_joint_ref_button)
        self.remove_joint_ref_button.clicked.connect(self.remove_joint_ref_click)
        
        self.joint_ref_label = QtGui.QLabel('Add / remove joint ref group')
        self.joint_ref_horiz_layout.addWidget(self.joint_ref_label)
        self.joint_ref_horiz_layout.addStretch()

        
        # share hairsystem
        self.share_hairsystem_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.share_hairsystem_horiz_layout)
        
        self.share_hairsystem_checkbox = QtGui.QCheckBox()
        self.share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_checkbox)
        
        self.share_hairsystem_label = QtGui.QLabel('Share Hairsystem')
        self.share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_label)
        self.share_hairsystem_horiz_layout.addStretch()
          
        #self.vertical_layout.addStretch()

        # Setup
        self.setup_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.setup_horiz_layout)
        
        self.setup_button = QtGui.QPushButton('Setup Tendrils')
        self.setup_button.setMinimumWidth(125)
        self.setup_horiz_layout.addStretch()
        self.setup_horiz_layout.addWidget(self.setup_button)
        self.setup_button.clicked.connect(self.setup_tendril)
        
        
        
        

    def add_joint_ref_click(self):
        

        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a camera!')
            return

        
        for sel in sel_list:
        
            if not isinstance(sel, pm.nodetypes.Transform):
                pm.warning('{0} is not a valid transform, skipped'.format(sel.name()))
                continue
            
            item = QtGui.QStandardItem(sel.name())
            
            # set flags
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            self.model.appendRow(item) 
                
    
    def remove_joint_ref_click(self):
        
        selection_model = self.tree_view.selectionModel()
        
        # returns QModelIndex
        selected_rows = selection_model.selectedRows()
        
        row_list = [sel.row() for sel in selected_rows]
        row_list.sort(reverse=True)
        
        for row in row_list:
            self.model.removeRow(row)
    
       
    def setup_tendril(self):
        
        ref_grp_list = []
        
        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
        share_hairsystem = self.share_hairsystem_checkbox.isChecked()
        
        if num_children < 1:
            pm.warning('No joint ref are available in the treeview!')
            return
    
        for i in range(num_children):
            
            child = root.child(i)
            
            if child.checkState():
                
                ref_grp_list.append(child.text())
                

        name = self.name_line_edit.text()
        
        
        
        ref_list = []
        name_list = []
        
        for index, ref_grp in enumerate(ref_grp_list):
            
            ref_list.append(pm.PyNode(ref_grp))
            name_list.append('name_{0}'.format(index))
            
            
        
        # build the joints
        jnt_dict_list = build_joints(joint_ref_list=ref_list, name_list=name_list)
        
        
        # set up the nhair dynamics
        output_curve_list = []
        output_curve_set = pm.sets(name='output_curve_set') 
        
        
        
        #print(share_hairsystem)
        
        for index, jnt_dict in enumerate(jnt_dict_list):

            if index is 0:
                dyn_joint_dict = setup_dynamic_joint_chain(jnt_dict, ctrl_size=1.2)
                hairsystem = dyn_joint_dict.get('hairsystem')
    
            else:
                
                if share_hairsystem:
                    dyn_joint_dict = setup_dynamic_joint_chain(jnt_dict, existing_hairsystem=hairsystem, ctrl_size=1.2)
                    print('Use existing hairsystem')
                    
                else:
                    dyn_joint_dict = setup_dynamic_joint_chain(jnt_dict)
                    print('Create new hairsystem')
                    
                
            output_curve_list.append(dyn_joint_dict.get('output_curve'))
            add_pocedural_wave_anim(dyn_joint_dict, ctrl_size=1)
    
        
        output_curve_set.addMembers(output_curve_list)
        


def show():      
    win = Import_nuke_2d_track_ui(parent=maya_main_window())
    win.show()
    
#show()    