#node_list = cmds.ls(sl=True)
node_list = pm.ls()

object_id_list = []
mat_id_list = []
op_id_list = []


for node in node_list:
    
    if isinstance(node, pm.nodetypes.VRayObjectProperties):
        if node.objectIDEnabled.get():
            op_id_list.append(node)
        
    elif pm.attributeQuery('vrayObjectID', exists=True, node=node):
        object_id_list.append(node)
        
    elif pm.attributeQuery('vrayMaterialId', exists=True, node=node):
        mat_id_list.append(node)