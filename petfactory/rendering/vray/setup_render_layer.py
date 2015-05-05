import pprint
import maya.cmds as cmds

def create_layer_override(node, attr_dict, layer):
    
    overide_attr_list = ['{0}.{1}'.format(node, attr) for attr in attr_dict.keys()]
    
    # create layer override
    pm.editRenderLayerAdjustment(overide_attr_list, layer=layer)   
    
    for attr, value in attr_dict.iteritems():
        #print(attr, value)
        pm.setAttr('{0}.{1}'.format(node, attr), value)
    
                                

def set_attr(node, attr_dict, layer):
    
    for attr, value in attr_dict.iteritems():
        pm.setAttr('{0}.{1}'.format(node, attr), value)
        
        

def set_render_element_override(render_element_dict, override_dict):
    
    for name, value in override_dict.iteritems():
        
        render_element = render_element_dict.get(name)
        
        if render_element is None:
            pm.warning('did not find render element, continue')
            continue
        
        try:
            render_element = pm.PyNode(render_element)
            
        except pm.MayaNodeError as e:
            pm.warning(e) 
        
        # create layer override
        pm.editRenderLayerAdjustment('{0}.enabled'.format(render_element))

        # set attr 
        render_element.enabled.set(value)
        

def setup_render_layers():

    # just a remainder to assign the environt material to the environt on the truck and trailer layer.
    try:
        environment_material = pm.PyNode('environment_material')
        
    except pm.MayaNodeError as e:
        pm.warning('Please make sure that a vray material called environment_material exists. White diffuse, no reflection')
        return
    
    if not isinstance(environment_material, pm.nodetypes.VRayMtl):
        pm.warning('Please make sure that a vray material called environment_material exists. White diffuse, no reflection')
        return
        
    
    
    render_element_string_dict = {
    'multimatte_1':'MultiMatteElement',
    'multimatte_2':'MultiMatteElement',
    'multimatte_3':'MultiMatteElement',
    'multimatte_4':'MultiMatteElement',
    'lighting':'lightingChannel',
    'gi':'giChannel',
    'reflection':'reflectChannel',
    'refraction':'refractChannel',
    'specular':'specularChannel',
    'contact_ao':'ExtraTexElement'}
    
    
    
    # add render elements
    render_element_dict = {}
    
    for render_element_name, class_name in render_element_string_dict.iteritems():
        render_element_unicode = mel.eval('vrayAddRenderElement {0}'.format(class_name))
        render_element = pm.PyNode(render_element_unicode)
        render_element_dict[render_element_name] = render_element
        render_element.setName(render_element_name)
        
        if class_name == 'MultiMatteElement':
            render_element.vray_name_multimatte.set(render_element_name)
    
    
    
    # set multimatte attr
    multimatte_list = []
    multimatte_list.append(render_element_dict.get('multimatte_1'))
    multimatte_list.append(render_element_dict.get('multimatte_2'))
    multimatte_list.append(render_element_dict.get('multimatte_3'))
    multimatte_list.append(render_element_dict.get('multimatte_4'))
    
    for index, multimatte in enumerate(multimatte_list):
       
        multimatte.vray_usematid_multimatte.set(1)
        multimatte.vray_redid_multimatte.set(index*3+1)
        multimatte.vray_greenid_multimatte.set(index*3+2)
        multimatte.vray_blueid_multimatte.set(index*3+3)
        
          
    # add env render layer
    pm.select('|bridge_main_grp')
    env_render_layer = pm.createRenderLayer(name='env')
    
    
    # add truck render layer
    pm.select('P2952_FH13_Enhanced_Plus', '|bridge_main_grp', 'ref_trailer_2952_v003:trailer_main_grp', 'VRayLightDome1')
    truck_trailer_render_layer = pm.createRenderLayer(name='truck_trailer')
    
    
    # add contact ao render layer
    pm.select('P2952_FH13_Enhanced_Plus', '|bridge_main_grp|render_road_grp', 'ref_trailer_2952_v003:trailer_main_grp')
    contact_ao_render_layer = pm.createRenderLayer(name='contact_ao')
    
    
                                    
    
    
    # truck_trailer_render_layer
    
    truck_trailer_render_layer_vray_op_bridge_garage_dict = {
    'giVisibility':0,
    'primaryVisibility':0,
    'useIrradianceMap':0,
    'generateGI':0,
    'receiveGI':0,
    'generateCaustics':0,
    'receiveCaustics':0}
    
    
    truck_trailer_render_layer_vray_op_render_road_dict = {
    'matteSurface':1,
    'alphaContribution':-1}
      
      
    truck_trailer_render_layer_render_element_dict = {
    'multimatte_1':1,
    'multimatte_2':1,
    'multimatte_3':1,
    'multimatte_4':1,
    'lighting':1,
    'gi':1,
    'reflection':1,
    'refraction':1,
    'specular':1,
    'contact_ao':0}
    
    
    # contact_ao_render_layer
    
    contact_ao_render_layer_multi_op_dict = {
    'giVisibility':0,
    'primaryVisibility':0,
    'useIrradianceMap':0,
    'generateGI':0,
    'receiveGI':0,
    'generateCaustics':0,
    'receiveCaustics':0,
    'giVisibility':0,
    'primaryVisibility':0,
    'reflectionVisibility':0,
    'refractionVisibility':0,
    'shadowVisibility':0}
    
    contact_ao_render_layer_render_element_dict = {
    'multimatte_1':0,
    'multimatte_2':0,
    'multimatte_3':0,
    'multimatte_4':0,
    'lighting':0,
    'gi':0,
    'reflection':0,
    'refraction':0,
    'specular':0,
    'contact_ao':1}
    
    
    # env_render_layer
    
    env_render_layer_render_element_dict = {
    'multimatte_1':0,
    'multimatte_2':0,
    'multimatte_3':0,
    'multimatte_4':0,
    'lighting':0,
    'gi':0,
    'reflection':0,
    'refraction':0,
    'specular':0,
    'contact_ao':0}
    
    
    
    
    # create overrides
    # ----------------------------------------------------
    
    # truck_trailer_render_layer
    
    pm.editRenderLayerGlobals(currentRenderLayer=truck_trailer_render_layer)
    
    
    create_layer_override(  node = 'vray_op_bridge_garage',
                            attr_dict = truck_trailer_render_layer_vray_op_bridge_garage_dict,               
                            layer = truck_trailer_render_layer)
                            
                              
    create_layer_override(  node='vray_op_render_road',
                            attr_dict = truck_trailer_render_layer_vray_op_render_road_dict,              
                            layer=truck_trailer_render_layer)
    
    
    set_render_element_override(render_element_dict=render_element_dict, override_dict=truck_trailer_render_layer_render_element_dict)
    
    
    # contact_ao_render_layer
    
    pm.editRenderLayerGlobals(currentRenderLayer=contact_ao_render_layer)
    
    create_layer_override(  node='vray_op_FH13_Enhanced_Plus_body',
                            attr_dict = contact_ao_render_layer_multi_op_dict,
                            layer=contact_ao_render_layer)
    
    create_layer_override(  node='vray_op_FH13_Enhanced_Plus_wheels',
                            attr_dict = contact_ao_render_layer_multi_op_dict,
                            layer=contact_ao_render_layer)
                            
    create_layer_override(  node='vray_op_FH13_Enhanced_Plus_headlamps',
                            attr_dict = contact_ao_render_layer_multi_op_dict,
                            layer=contact_ao_render_layer)
                            
    create_layer_override(  node='vray_op_FH13_Enhanced_Plus_windshield',
                            attr_dict = contact_ao_render_layer_multi_op_dict,
                            layer=contact_ao_render_layer)
                            
                                                                          
    create_layer_override(  node='ref_trailer_2952_v003:vray_op_trailer_body',
                            attr_dict = contact_ao_render_layer_multi_op_dict,
                            layer=contact_ao_render_layer)
                            
                            
    create_layer_override(  node='ref_trailer_2952_v003:vray_op_trailer_wheels',
                            attr_dict = contact_ao_render_layer_multi_op_dict,
                            layer=contact_ao_render_layer)
                            
    
    set_render_element_override(render_element_dict=render_element_dict, override_dict=contact_ao_render_layer_render_element_dict)
    
     
     
    # contact_ao_render_layer
    
    pm.editRenderLayerGlobals(currentRenderLayer=env_render_layer)
    set_render_element_override(render_element_dict=render_element_dict, override_dict=env_render_layer_render_element_dict)
    
                         
    #pprint.pprint(dir(contact_ao_render_layer))
    #pprint.pprint(contact_ao_render_layer.listAdjustments())


setup_render_layers()