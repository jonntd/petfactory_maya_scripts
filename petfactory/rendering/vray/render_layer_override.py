import pymel.core as pm

def create_layer_override(enabled=True):

    render_element_list = pm.ls(type="VRayRenderElement")
    
    for render_element in render_element_list:
    
        # create layer override
        pm.editRenderLayerAdjustment('{0}.enabled'.format(render_element))
        
        # enable the layer
        render_element.enabled.set(enabled)


def create_layer_override_off():
    create_layer_override(enabled=False)


def create_layer_override_on():
    create_layer_override(enabled=True)


def remove_layer_override(enabled=True):

    render_element_list = pm.ls(type="VRayRenderElement")

    for render_element in render_element_list:

        pm.editRenderLayerAdjustment('{0}.enabled'.format(render_element), remove=True)

        # enable the layer
        render_element.enabled.set(enabled)

def remove_layer_override_off():
    remove_layer_override(enabled=False)


def remove_layer_override_on():
    remove_layer_override(enabled=True)