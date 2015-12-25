import pymel.core as pm


attrKey = 'objExportName'

 
def gather_meshes():
    
    mesh_list = pm.ls(type='mesh')
    match_list = []
    
    for mesh in mesh_list:
        
        if pm.attributeQuery(attrKey, node=mesh, exists=True):
            
            #attr = pm.getAttr('{}.{}'.format(mesh, attrKey))
            match_list.append(mesh)
            print('attr found on: {}'.format(mesh))
                
    return match_list


def addMeshAttr(attrValue):
    
    sel_list = pm.ls(sl=True)
    count = 0
    
    for sel in sel_list:
        
        try:
            shape = sel.getShape()
            
            # if the attr does not exist create it
            if not pm.attributeQuery(attrKey, node=shape, exists=True):
            
                pm.addAttr(shape, ln=attrKey, dt='string')
            
            pm.setAttr('{}.{}'.format(shape, attrKey), attrValue)
            count += 1
    
        except AttributeError as e:
            #print(e)
            pass
            
    print('the attr "{}" was set to: "{}" on {} meshe(s)'.format(attrKey, attrValue, count))
    

def export_mesh_with_attr():
    
    match_list = gather_meshes()
    
    mesh_attr_dict = {}
    export_mesh_list = []
    
    for mesh in mesh_list:
        
        attr = pm.getAttr('{}.{}'.format(mesh, attrKey))
        
        if attr not in mesh_attr_dict:
            mesh_attr_dict[attr] = []
            
        mesh_attr_dict[attr].append(mesh)
        
    #return mesh_attr_dict
    
    
    for attr, mesh_list in mesh_attr_dict.iteritems():
        
        dup_list = []
        #print(attr)
        for mesh in mesh_list:
            dup = mesh.duplicate()
            dup_list.append(dup)
        
        if len(dup_list) > 1:
            combined_mesh = pm.polyUnite(dup_list, n=attr, ch=False )[0]
        else:
            combined_mesh = dup_list[0]
            
        pm.polyTriangulate(combined_mesh, ch=False)
        export_mesh_list.append(combined_mesh)
        
        
    pm.select(export_mesh_list)
    pm.exportSelected('/Users/johan/Desktop/puppe.obj', force=True, typ='OBJexport', op="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")
    
    #pm.delete()

#addMeshAttr('yellow')

#match_list = gather_meshes()
sort_mesh_by_attr(match_list)
