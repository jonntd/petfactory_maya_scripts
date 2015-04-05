import re
#import pprint

def create_set_from_regex(pattern, nodetype, use_longname, use_parent, set_name):
    
    node_list = pm.ls(type=nodetype)
    
    match_list = []
    for node in node_list:
        
        if use_parent:
            
            try:
                node = node.getParent()
                
            except AttributeError as e:
                pm.warning(e)
                continue

        if use_longname:
            name = node.longName()
        else:
            name = node.nodeName()         
        #print(name)
        
        match_obj = re.match(pattern, name)
        if match_obj:
            match_list.append(node)

    #pprint.pprint(match_list)
    pm.select(deselect=True)
    mesh_set = pm.sets(name='{0}_set'.format(set_name))
    mesh_set.addMembers(match_list)
    


pattern = r'^[\w\d|]*weld[\w\d|]*$'
nodetype = pm.nodetypes.Mesh
use_longname = True
use_parent = True
set_name = 'weld'


create_set_from_regex(  pattern=pattern,
                        nodetype=nodetype,
                        use_longname=use_longname,
                        use_parent=use_parent,
                        set_name=set_name)

