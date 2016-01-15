import xml.etree.ElementTree as ET
import pymel.core as pm

path = r'/Users/johan/Dev/maya/petfactory_maya_scripts/petfactory/scene/recursive_hierarchy/test.xml'
valid_types = ['group', 'switch']

def xml_recurse_maya(xml_node, parent=None, depth=-1):

	name = xml_node.get('name')	
	node_type = xml_node.get('type')
	
	node = pm.group(em=True, name='{}'.format(name))
	
	if parent:
	    pm.parent(node, parent)
	    #print(node, parent)
		
	print('{} {} {}'.format(depth*'\t', name, node_type))
	
	depth += 1

	if node_type not in valid_types:
		print('not a valid type, raise error!')
		
	children = xml_node.getchildren()

	if children:
		for child in children:
			xml_recurse_maya(child, node, depth)


tree = ET.parse(path)
root = tree.getroot()
xml_recurse_maya(root)