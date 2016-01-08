#canvas_node = pm.PyNode('canvasNode1')

def buildMeshOutput():
    
    mesh_list = []
    
    sel_list = pm.ls(sl=True)
    
    for sel in sel_list:
        
        canvas_node = sel
        
        attr_list = canvas_node.listAttr(userDefined=True, settable=True, readOnly=True)
        
        
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