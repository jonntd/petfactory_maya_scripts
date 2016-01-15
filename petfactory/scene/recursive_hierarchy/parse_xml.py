import xml.etree.ElementTree as ET

valid_types = ['group', 'switch']

def xml_recurse(node, depth):

	name = node.get('name')
	node_type = node.get('type')
	print('{} {} {}'.format(depth*'\t', name, node_type))
	depth += 1

	if node_type not in valid_types:
		print('not a valid type, raise error!')
	children = node.getchildren()

	if children:
		for child in children:
			xml_recurse(child, depth)


tree = ET.parse('test.xml')
root = tree.getroot()

xml_recurse(root, -1)