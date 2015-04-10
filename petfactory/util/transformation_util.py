import pymel.core as pm


def pos_on_curve(crv, num_pos, start_offset=0.0, end_offset=0.0, u_param_list=None):
    
    crv_shape = crv.getShape()
    crv_length = crv_shape.length()
    length = crv_length * (1.0-start_offset-end_offset)
    start_length_offset = crv_length * start_offset
    
    # if a u_param_list is givem make sure that it has the correct length
    if u_param_list is not None:
            
        if len(u_param_list) != num_pos:
            pm.warning('The length of the u_param_list must be {}'.format(num_pos))
            return None
        
    # no joint_u_list were provided, calculate even spacing
    else:
        
        length_inc = 1.0 / (num_pos-1)
        u_param_list = []
        for n in range(num_pos):
            u_param_list.append(length_inc*n)
    

    pos_list = []
    for index in range(num_pos):
        
        u = crv_shape.findParamFromLength(u_param_list[index]*length+start_length_offset)
        p = crv_shape.getPointAtParam(u, space='world')
        pos_list.append(p)
        
    return pos_list
        


def create_curve_from_pos_list(pos_list, show_cvs=False):
    
    crv = pm.curve(d=3, p=pos_list)
    
    if show_cvs:
        pm.toggle(crv, cv=True)
        
    return crv
 
def create_curve_from_curve(crv, num_pos, start_offset=0.0, end_offset=0.0, u_param_list=None, show_cvs=False):

    pos_list = pos_on_curve(crv = crv,
                            num_pos = num_pos,
                            start_offset = start_offset,
                            end_offset = end_offset,
                            u_param_list = u_param_list)
                            
    if pos_list is not None:                   
        return create_curve_from_pos_list(pos_list, show_cvs)
        
    else:
        return None
 
'''
crv = pm.PyNode('curve1')
num_pos = 13
u_param_list = None
start_offset = 0
end_offset = 0
show_cvs = True

create_curve_from_curve(crv, num_pos, start_offset, end_offset, u_param_list, show_cvs)
'''
