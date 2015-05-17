import maya.mel as mel
import pymel.core as pm
import pprint


def add_multimate_range(num_multimatte, start_index=0, use_mat_id=True):
    
    ret_dict = {}
    
    for element_index in range(num_multimatte):
        
        render_element_unicode = mel.eval('vrayAddRenderElement MultiMatteElement')
        render_element = pm.PyNode(render_element_unicode)
        
        first_index = element_index*3 + start_index
        
        name = 'multimatte_{0}_{1}_{2}'.format(first_index, first_index+1, first_index+2)
        
        if pm.objExists(name):
            pm.warning('Render element "{0}" exists'.format(name))
            name = '{}_dup'.format(name)
            
        render_element.vray_name_multimatte.set(name)
        render_element.setName(name)
        
        if use_mat_id:
            render_element.vray_usematid_multimatte.set(1)
        
        render_element.vray_redid_multimatte.set(first_index)
        render_element.vray_greenid_multimatte.set(first_index+1)
        render_element.vray_blueid_multimatte.set(first_index+2)
        
        ret_dict[name] = render_element
        
    return ret_dict
        

def add_render_element(string_dict):
    
    # add render elements
    render_element_dict = {}
    
    for render_element_name, class_name in render_element_string_dict.iteritems():
        render_element_unicode = mel.eval('vrayAddRenderElement {0}'.format(class_name))
        render_element = pm.PyNode(render_element_unicode)
        render_element_dict[render_element_name] = render_element
        render_element.setName(render_element_name)
        
    return render_element_dict
        
               

def inspect_mm():
    
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
            
    
    #print(object_id_list)
    if object_id_list: 
        object_ids = [n.objectID.get() for n in object_id_list]
        object_ids.sort()
        print('object ids')
        print(object_ids)
        
    #print(op_id_list)
    if op_id_list:
        object_prop_ids = [n.objectID.get() for n in op_id_list]
        object_prop_ids.sort()
        print('op ids')
        print(object_prop_ids.sort())
       
    #print(mat_id_list)
    if mat_id_list:
        mat_ids = [n.vrayMaterialId.get() for n in mat_id_list]
        mat_ids.sort()
        print('mat ids')
        print(mat_ids)
        pprint.pprint([n for n in mat_id_list])

    

render_element_string_dict = {
'lighting':'lightingChannel',
'gi':'giChannel',
'reflection':'reflectChannel',
'refraction':'refractChannel',
'specular':'specularChannel',
'contact_ao':'ExtraTexElement'}

# create some render elements
render_element_dict = add_render_element(render_element_string_dict)

# create the mm passes, add to the render_element_dict
mm_dict = add_multimate_range(11, start_index=1)
render_element_dict.update(mm_dict)

#render_element_unicode = mel.eval('vrayRemoveRenderElement multimatte_1_3')

#inspect_mm()
