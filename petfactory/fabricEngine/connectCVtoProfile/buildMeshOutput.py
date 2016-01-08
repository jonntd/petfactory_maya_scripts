

def buildMeshOutput():

    sel_list = pm.ls(sl=True)
    mesh_list = []
    
    for sel in sel_list:
        
        if not isinstance(sel, pm.nodetypes.CanvasNode):
            print('"{}" is not a canvas node, skipping...'.format(sel))
            continue
        
        attr_list = sel.listAttr(userDefined=True, settable=True, readOnly=True)
                
        for attr in attr_list:
            
            if attr.type() != 'mesh':
                continue
                
            attr_name = attr.name(includeNode=False)
            mesh = pm.createNode('mesh')
            attr >> mesh.inMesh
            dup_mesh = pm.duplicate(mesh)
            mesh_list.append(dup_mesh)
            attr // mesh.inMesh
            pm.delete(mesh.getParent())
        
    pm.select(mesh_list)
    

buildMeshOutput()