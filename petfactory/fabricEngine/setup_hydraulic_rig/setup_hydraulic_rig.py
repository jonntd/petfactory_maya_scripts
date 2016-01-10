

def setup_hydraulic(loc_top, loc_btm, mesh_top, mesh_btm, create_instance=False):
    
    canvas_node = pm.createNode('canvasNode')
    path = '/Users/johan/Dev/fabricEngine/canvas/rigging/hydraulic/hydraulicMatrix.canvas'
    pm.dfgImportJSON(m=canvas_node, f=path)

    loc_top.worldMatrix >> canvas_node.inTopMatrix
    loc_btm.worldMatrix >> canvas_node.inBtmMatrix
    
    decompose_matrix_top = pm.createNode('decomposeMatrix', n='decomposeMatrix_top')
    decompose_matrix_btm = pm.createNode('decomposeMatrix', n='decomposeMatrix_btm')
    
    canvas_node.outTopMatrix >> decompose_matrix_top.inputMatrix
    canvas_node.outBtnMatrix >> decompose_matrix_btm.inputMatrix
    
    
    if create_instance:
        
        shape_top = mesh_top.getShape()
        shape_btm = mesh_btm.getShape()
        
        mesh_top = pm.group(em=True, name='hydraulicMeshTop')
        mesh_btm = pm.group(em=True, name='hydraulicMeshBtm')
        
        pm.parent(shape_top, mesh_top, add=True, shape=True)
        pm.parent(shape_btm, mesh_btm, add=True, shape=True)
        

    decompose_matrix_top.outputTranslate >> mesh_top.translate
    decompose_matrix_top.outputRotate >> mesh_top.rotate
    
    decompose_matrix_btm.outputTranslate >> mesh_btm.translate
    decompose_matrix_btm.outputRotate >> mesh_btm.rotate

    


def do_setup():

    sel_list = pm.ls(sl=True)

    if len(sel_list) < 4:
        pm.warning('Select 2 locators and two meshes')
        return

    setup_hydraulic(sel_list[0], sel_list[1], sel_list[2], sel_list[3], create_instance=True)

#pm.select(['locator1', 'locator2', 'pCube1', 'pCube2'])
do_setup()