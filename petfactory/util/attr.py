import pymel.core as pm
import json

def set_json_attr(node, info_dict):

    json_data = json.dumps(info_dict)
    
    # if attr exists
    if pm.attributeQuery('json', node=node, exists=True):
        node.json.unlock()
        pm.deleteAttr(node, at='json')
        
    
    #else:
    pm.addAttr(node, ln='json', dt='string', k=False)
    node.json.set('{0}'.format(json_data))
    node.json.lock()


def get_json_attr(node):
    
    # if attr exists
    if pm.attributeQuery('json', node=node, exists=True):
        attr_string = node.getAttr('json')
        
        try:
            info_dict = json.loads(attr_string)
            
        except ValueError as e:
            pm.warning('Could not read the json attr, {0}'.format(e))
            return None
        
        return info_dict
            
    else:
        pm.warning('json attr does not exist!')
        return None
        
    
'''   
node = pm.PyNode('curve1')

info_dict = {'num_joints':2}
info_dict['radius'] = 2.2
set_json_attr(node, info_dict)

a = get_json_attr(node)
print(a)
'''