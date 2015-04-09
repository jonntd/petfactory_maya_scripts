import pymel.core as pm

import petfactory.util.vector as pet_vector
reload(pet_vector)

def create_joints_on_axis(num_joints=10, parent_joints=False, show_lra=True, name='joint', spacing=1, axis=0):
    
    jnt_list = []
    for index in range(num_joints):
        
        jnt = pm.createNode('joint', name='{0}_{1}_jnt'.format(name, index), ss=True)
        pos = (spacing*index, 0, 0)
        jnt.translate.set(pos)
        jnt_list.append(jnt)
        
        if show_lra:
            pm.toggle(jnt, localAxis=True)
            
    
    if parent_joints:
        parent_joint_list(jnt_list)
    
    return jnt_list
    
def create_joints_on_curve(crv, num_joints, up_axis, parent_joints=True, show_lra=True, name='joint', start_offset=0, end_offset=0, joint_u_list=None):
    

    if joint_u_list is not None:
        
        if len(joint_u_list) != num_joints-1:
            pm.warning('The length of the joint_u_list must be {}'.format(num_joints-1))
            return
            
        u_sum = float(sum(joint_u_list))
        print(u_sum)
        
        length_inc_list = []
        length_inc = 0
        for n in range(num_joints):
            if n > 0:
                length_inc += joint_u_list[n-1]/u_sum
            length_inc_list.append(length_inc)
                    
    else:
        
        length_inc = 1.0 / (num_joints-1)
        length_inc_list = []
        for n in range(num_joints):
            length_inc_list.append(length_inc*n)
    
    print(length_inc_list)
    
    crv_shape = crv.getShape()
    crv_length = crv_shape.length()
    length = crv_length * (1.0-start_offset-end_offset)
    start_length_offset = crv_length * start_offset
    
    
          
    crv_matrix = crv.getMatrix(worldSpace=True) 
    up_vec = pm.datatypes.Vector(crv_matrix[up_axis][0], crv_matrix[up_axis][1], crv_matrix[up_axis][2])
    up_vec.normalize()
    
    
    jnt_list = []
    for index in range(num_joints):
        
        print(length_inc_list[index])
        
        #u = crv_shape.findParamFromLength(length_inc_list[index]*index+start_length_offset)
        u = crv_shape.findParamFromLength(length_inc_list[index]*length+start_length_offset)
        #u = crv_shape.findParamFromLength(length_inc*index+start_length_offset)
        p = crv_shape.getPointAtParam(u, space='world')
        jnt = pm.createNode('joint', name='{0}_{1}_jnt'.format(name, index), ss=True)
        jnt.translate.set(p)
        jnt_list.append(jnt)
        
        if index > 0:
            
            prev_jnt = jnt_list[index-1].getTranslation(space='world')
            curr_jnt = jnt_list[index].getTranslation(space='world')
            
            aim_vec = (curr_jnt - prev_jnt).normal()  
            
            if aim_vec.isParallel(up_vec, tol=0.1):
                pm.warning('up_vec is to close to the aim vec')
            
            # build a transform matrix from aim and up
            tm = pet_vector.remap_aim_up(aim_vec, up_vec, aim_axis=0, up_axis=2, invert_aim=False, invert_up=False, pos=prev_jnt)
            
            pm_rot = tm.getRotation()
            r_deg = pm.util.degrees((pm_rot[0], pm_rot[1], pm_rot[2]))
                                    
            if index is num_joints-1:
                jnt_list[index-1].jointOrient.set(r_deg)
                jnt_list[index].jointOrient.set(r_deg)
    
            else:
                jnt_list[index-1].jointOrient.set(r_deg)
                
                
        if show_lra:
            pm.toggle(jnt, localAxis=True)
                
                
    if parent_joints:
        parent_joint_list(jnt_list)
    
    return jnt_list
            
            
def parent_joint_list(joint_list):         
    for index, jnt in enumerate(joint_list):
        if index > 0:
            pm.parent(joint_list[index], joint_list[index-1])
    pm.select(deselect=True)
    