import xml.etree.ElementTree as ET

path = r'/Users/johan/Dev/maya/petfactory_maya_scripts/petfactory/scene/recursive_hierarchy/test.xml'
valid_types = ['group', 'switch']

def xml_recurse_string(node, parent=None, depth=-1):

	name = node.get('name')
	parent_name = parent.get('name') if parent else 'None'
	node_type = node.get('type')
	print('{} {} {} -> parent: {}'.format(depth*'\t', name, node_type, parent_name))
	
	depth += 1

	if node_type not in valid_types:
		print('not a valid type, raise error!')
	children = node.getchildren()

	if children:
		for child in children:
			xml_recurse(child, node, depth)


tree = ET.parse(path)
root = tree.getroot()

xml_recurse(root)