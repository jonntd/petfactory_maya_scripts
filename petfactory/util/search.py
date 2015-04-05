import re
import pprint


pattern = r'^[\w\d|]*weld[\w\d|]*$'
nodetype = pm.nodetypes.Mesh
use_longname = True
use_shape = True
match_list = []
set_name = 'weld'
node_list = pm.ls(type='transform')

for node in node_list:
    
    if use_longname:
        name = node.longName()
    else:
        name = node.nodeName()         
    #print(name)
    
    match_obj = re.match(pattern, name)
    if match_obj:
        
        if use_shape:
            
            try:
                if isinstance(node.getShape(), nodetype):
                    match_list.append(node)
                
            except AttributeError as e:
                #pm.warning('Select a transform to use the getShape method. {0}'.format(e))
                continue
        else:
            match_list.append(node)
            

#pprint.pprint(match_list)

pm.select(deselect=True)
mesh_set = pm.sets(name='{0}_set'.format(set_name))
mesh_set.addMembers(match_list)