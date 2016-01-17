import xml.etree.ElementTree as ET
import pprint

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class NameError(Error):
    pass

class AttributeError(Error):
    pass

class ValueError(Error):
    pass

required_attrib = [ 'name',
                    'nodeType',
                    'prefix',
                    'sectionInSGUI']

def validate_XML(node):

    name = node.get('name')
    if name == '':
        raise NameError('the node has no name!')

    # make sure that all the required attributes exist and validate their values
    attrbs = node.attrib
    for attrb, value in attrbs.iteritems():
        if not attrb in required_attrib:
            raise AttributeError('Unexpected attribute: "{}" in node: "{}"'.format(attrb, name))

        if attrb == 'nodeType':
            if value.upper() == 'GROUP':
                nodeType = "Group"
            elif value.upper() == 'SWITCH':
                nodeType = "Switch"
            else:
                raise ValueError('Unexpected value: "{}" of attribute: "{}" in node: "{}"'.format(value, attrb, name))


        if attrb == 'prefix':
            if value.upper() == '':
                geoType = None
            elif value.upper() == 'INT':
                geoType = 'INT'
            elif value.upper() == 'EXT':
                geoType = 'EXT'
            else:
                raise ValueError('Unexpected value: "{}" of attribute: "{}" in node: "{}"'.format(value, attrb, name))


        if attrb == 'sectionInSGUI':
            try:
                sectionInSGUI = int(value)
            except ValueError as e:
                raise ValueError('Unexpected value: "{}" of attribute: "{}" in node: "{}"'.format(value, attrb, name))

    # recurse
    children = node.getchildren()
    if children:
        for child in children:
            validate_XML(child)


def getOrganizeSceneGraphInfo(node, info_dict):

    name = node.get('name')
    sectionInSGUI = int(node.get('sectionInSGUI'))

    # get info of placement inte organize scenegraph UI
    if sectionInSGUI > 0:

        if sectionInSGUI not in info_dict:
            info_dict[sectionInSGUI] = []

        info_dict[sectionInSGUI].append(name)

    # recurse
    children = node.getchildren()
    if children:
        for child in children:
            getOrganizeSceneGraphInfo(child, info_dict)

    return info_dict

def mayaXML(xml_node, parent=None, depth=-1):

    name = xml_node.get('name') 
    nodeType = xml_node.get('nodeType')
    switch_prefix = 'G__' if nodeType.upper() == 'SWITCH' else ''
    prefix = xml_node.get('prefix')
    prefix = prefix if prefix == '' else '{}_'.format(prefix)  
    nodeName = '{}{}{}'.format(switch_prefix, prefix, name)
    print('{}{}'.format(depth*'\t', nodeName))

    node = pm.group(em=True, name=nodeName)

    if parent:
        pm.parent(node, parent)

    depth += 1

    children = xml_node.getchildren()
    if children:
        for child in children:
            mayaXML(child, node, depth)


def createVredScenegraph(XMLpath):

    tree = ET.parse(XMLpath)
    validate_XML(tree.getroot())
    #mayaXML(tree.getroot())

def createOrganizeVredUI(XMLpath):

    tree = ET.parse(XMLpath)
    validate_XML(tree.getroot())

    info_dict = {}
    getOrganizeSceneGraphInfo(tree.getroot(), info_dict)

    keys = info_dict.keys()
    keys.sort()

    for index, key in enumerate(keys):
        name_list = info_dict[key]
        if index > 0:
            print('--------')
        for name in name_list:
            print(name)


path = r'/Users/johan/Dev/maya/petfactory_maya_scripts/petfactory/scene/recursive_hierarchy/nodeWithAttrib.xml'

createVredScenegraph(path)

createOrganizeVredUI(path)

