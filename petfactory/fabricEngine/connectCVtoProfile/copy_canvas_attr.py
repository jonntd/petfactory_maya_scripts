def get_attr_dict(canvas_node, allowed_attr):
    
    user_defined_attr = canvas_node.listAttr(userDefined=True, settable=True)               
    attr_dict = {}
    
    for attr in user_defined_attr:
                
        try:
            index = allowed_attr.index(attr.type())
            
            # Check if the plug is a child plug.
            # A child plug’s parent is always a compound plug.
            if attr.isChild():
                continue
           
            attr_dict[attr.name(includeNode=False)] = attr.get()
            
        except ValueError:
            pass
            
    return attr_dict


def set_attr_dict(canvas_node, attr_dict):
    
    for attr, value in attr_dict.iteritems():
        
        try:
            pm.setAttr('{}.{}'.format(canvas_node, attr), value)
            
        except pm.MayaAttributeError as e:
            print('could not set attr. {}'.format(e))
 
    
def copy_canvas_attr(canvas_from, canvas_to):
    
    valid_attr_type = ['bool', 'double', 'long']
    attr_dict = get_attr_dict(canvas_from, valid_attr_type)
    set_attr_dict(canvas_to, attr_dict)


def copy_from_sel():
    sel_list = pm.ls(sl=True)
    if len(sel_list) < 2:
        pm.warning('Please select 2 canvas nodes!')
        return
        
    if isinstance(sel_list[0], pm.nodetypes.CanvasNode) and isinstance(sel_list[1], pm.nodetypes.CanvasNode):
        copy_canvas_attr(sel_list[0], sel_list[1])
        
    else:
        pm.warning('Make sure that selected nodes are canvasNodes!')
    

copy_from_sel()

