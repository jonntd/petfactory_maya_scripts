import pymel.core as pm
    
def gather_meshes(attrKey, attrValue):
    
    mesh_list = pm.ls(type='mesh')
    match_list = []
    
    for mesh in mesh_list:
            
        transform = mesh.getParent()
        
        if transform:
            attr = pm.getAttr('{}.{}'.format(transform, attrKey))
            if attr == attrValue:
                match_list.append(transform)
                
                print('Match!: {}'.format(transform))
            else:
                print('no match: {}'.format(transform))
                
    return match_list
    
def addMeshAttr(attrKey, attrValue):
    
    sel_list = pm.ls(sl=True)
    
    for sel in sel_list:
        
        transform = sel.getParent()
        pm.addAttr(sel, ln=attrKey, dt='string')
        pm.setAttr('{}.{}'.format(sel, attrKey), attrValue)


attrKey = 'objExportName'
attrValue = 'ground'

addMeshAttr(attrKey, attrValue)

match_list = gather_meshes(attrKey, attrValue)

#pm.select(match_list)

# todo duplicate the meshes

combined_mesh = pm.polyUnite(match_list, n='result', ch=False )[0]
pm.polyTriangulate(combined_mesh, ch=False)