import maya.mel as mel
import pymel.core as pm


num_multimatte = 3

for element_index in range(num_multimatte):
    
    render_element_unicode = mel.eval('vrayAddRenderElement MultiMatteElement')
    render_element = pm.PyNode(render_element_unicode)
    render_element.setName('multimatte_{0}'.format(element_index+1))
  
    render_element.vray_usematid_multimatte.set(1)
    
    render_element.vray_redid_multimatte.set(element_index*3+1)
    render_element.vray_greenid_multimatte.set(element_index*3+2)
    render_element.vray_blueid_multimatte.set(element_index*3+3)
        
