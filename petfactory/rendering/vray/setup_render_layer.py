# add env render layer
pm.select('|bridge_main_grp')
env_render_layer = pm.createRenderLayer(name='env')


# add truck render layer
pm.select('P2952_FH13_Enhanced_Plus', '|bridge_main_grp', 'ref_trailer_2952_v003:trailer_main_grp', 'VRayLightDome1')
truck_trailer_render_layer = pm.createRenderLayer(name='truck_trailer')


# add contact ao render layer
pm.select('P2952_FH13_Enhanced_Plus', '|bridge_main_grp|render_road_grp', 'ref_trailer_2952_v003:trailer_main_grp')
contact_ao_render_layer = pm.createRenderLayer(name='contact_ao')


                                
def create_layer_override(node, attr_list, layer):
    
    overide_attr_list = ['{0}.{1}'.format(node, attr) for attr in attr_list]
    
    # create layer override
    pm.editRenderLayerAdjustment(overide_attr_list, layer=layer)
                                
    
create_layer_override(  node='vray_op_FH13_Enhanced_Plus_body',
                        attr_list = [   'giVisibility',
                                        'primaryVisibility',
                                        'reflectionVisibility',
                                        'refractionVisibility',
                                        'shadowVisibility'],
                        layer=contact_ao_render_layer)