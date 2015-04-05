import re
#import pprint

def create_set_from_regex(pattern, nodetype, use_longname, use_parent, set_name):
    
    try:
        regex = re.compile(pattern)
        
    except re.error as e:
        pm.warning(e)
        return None
    
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

        match_obj = regex.match('abcdef_weld_asas')
        if match_obj:
            match_list.append(node)

 
    if len(match_list) > 0:
        pm.select(deselect=True)
        mesh_set = pm.sets(name='{0}_set'.format(set_name))
        mesh_set.addMembers(match_list)
    else:
        pm.warning('No match found!')
    


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

