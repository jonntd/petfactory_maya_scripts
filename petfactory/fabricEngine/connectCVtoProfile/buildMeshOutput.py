

def buildMeshOutput():

    sel_list = pm.ls(sl=True)
   
    for sel in sel_list:
        
        if not isinstance(sel, pm.nodetypes.CanvasNode):
            print('"{}" is not a canvas node, skipping...'.format(sel))
            continue
        
        main_grp = pm.group(em=True)
        
        matrix = None
        name = None
        attr_list = sel.listAttr(userDefined=True, settable=True)
        
        for attr in attr_list:
            
            # skip compund attr
            if attr.isChild():
                continue
                
            if attr.type() == 'matrix':
                print('matrix')
                matrix = attr.get()
                main_grp.setMatrix(matrix)
                
                inputs = attr.inputs()
                if inputs:
                    name = inputs[0].name()
                    main_grp.rename('{}_grp'.format(name))
                                   
        attr_list = sel.listAttr(userDefined=True, settable=True, readOnly=True)
          
        for attr in attr_list:
            
            if attr.type() != 'mesh':
                continue
                  
            attr_name = attr.name(includeNode=False)
            mesh = pm.createNode('mesh')
            attr >> mesh.inMesh
            
            dup_trans = pm.duplicate(name='{}_mesh'.format(name))
            
            # break connection to the canvas node and delete
            attr // mesh.inMesh
            pm.delete(mesh.getParent())
            
            #mesh_trans = pm.group(em=True, name='{}_mesh'.format(name))
            #pm.parent(mesh, mesh_trans, shape=True, add=True)
            
            pm.parent(dup_trans, main_grp)
            
            
            

#pm.select('canvasNode2')
buildMeshOutput()