# add env render layer
pm.select('|bridge_main_grp')
env_render_layer = pm.createRenderLayer(name='env')


# add truck render layer
pm.select('P2952_FH13_Enhanced_Plus', '|bridge_main_grp', 'ref_trailer_2952_v003:trailer_main_grp', 'VRayLightDome1')
truck_trailer_render_layer = pm.createRenderLayer(name='truck_trailer')


# add contact ao render layer
pm.select('P2952_FH13_Enhanced_Plus', '|bridge_main_grp|render_road_grp', 'ref_trailer_2952_v003:trailer_main_grp')
contact_ao_render_layer = pm.createRenderLayer(name='contact_ao')


                                
def create_layer_override(node, attr_dict, layer):
    
    overide_attr_list = ['{0}.{1}'.format(node, attr) for attr in attr_dict.keys()]
    
    # create layer override
    pm.editRenderLayerAdjustment(overide_attr_list, layer=layer)
    #print(overide_attr_list)
    
    '''
    for attr, value in attr_dict.iteritems():
        #print(attr, value)
        pm.setAttr('{0}.{1}'.format(node, attr), value)
    '''
                                

def set_attr(node, attr_dict, layer):
    
    for attr, value in attr_dict.iteritems():
        pm.setAttr('{0}.{1}'.format(node, attr), value)


##################################
#
# truck_trailer_render_layer
#
##################################

# set overrides on the truck layer, bridge and garage vray prop
create_layer_override(  node='vray_op_bridge_garage',

                        attr_dict = {   'giVisibility':0,
                                        'primaryVisibility':0,
                                        'useIrradianceMap':0,
                                        'generateGI':0,
                                        'receiveGI':0,
                                        'generateCaustics':0,
                                        'receiveCaustics':0},
                                        
                        layer=truck_trailer_render_layer)
                        

# set overrides on the truck layer, bridge and garage vray prop
create_layer_override(  node='vray_op_render_road',

                        attr_dict = {   'matteSurface':1,
                                        'alphaContribution':-1},
                                        
                        layer=truck_trailer_render_layer)
                        
                        



##################################
#
# contact_ao_render_layer
#
##################################

contact_all_off_dict = {    'giVisibility':0,
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
                                        
# set overrides on the truck layer, bridge and garage vray prop
create_layer_override(  node='vray_op_FH13_Enhanced_Plus_body',
                        attr_dict = contact_all_off_dict,
                        layer=contact_ao_render_layer)
                        
create_layer_override(  node='ref_trailer_2952_v003:vray_op_trailer_body',
                        attr_dict = contact_all_off_dict,
                        layer=contact_ao_render_layer)
                        
                        
create_layer_override(  node='ref_trailer_2952_v003:vray_op_trailer_wheels',
                        attr_dict = contact_all_off_dict,
                        layer=contact_ao_render_layer)
                        



set_attr(   node='ref_trailer_2952_v003:vray_op_trailer_wheels',
            attr_dict = contact_all_off_dict,
            layer=contact_ao_render_layer)
                        