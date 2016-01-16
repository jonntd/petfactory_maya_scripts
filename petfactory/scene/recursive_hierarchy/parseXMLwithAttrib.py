import xml.etree.ElementTree as ET
import pprint

required_attrib = [ 'geoType',
                    'useInorganizeSGUI',
                    'nodeType',
                    'nodeName',
                    'sectionInSGUI']

def validate_XML(node):

    name = node.get('nodeName')
    if name == '':
        print('RaiseError, the node has no name!')
        raise

    # make sure that all the required attributes exist and validate their values
    attrbs = node.attrib
    for attrb, value in attrbs.iteritems():
        if not attrb in required_attrib:
            print('RaiseError, unexpected attribute! node: {}'.format(name))
            raise

        if attrb == 'geoType':
            if value.upper() == 'NONE':
                geoType = None
            elif value.upper() == 'INT':
                geoType = 'INT'
            elif value.upper() == 'EXT':
                geoType = 'EXT'
            else:
                print('RaiseError, unexpected value! node: {}'.format(name))
                raise

        if attrb == 'useInorganizeSGUI':
            if value.upper() == 'FALSE':
                useInorganizeSGUI = False
            elif value.upper() == 'TRUE':
                useInorganizeSGUI = True
            else:
                print('RaiseError, unexpected value! node: {}'.format(name))
                raise

        if attrb == 'nodeType':
            if value.upper() == 'GROUP':
                nodeType = "Group"
            elif value.upper() == 'SWITCH':
                nodeType = "Switch"
            else:
                print('RaiseError, unexpected value! node: {}'.format(name))
                raise

        if attrb == 'sectionInSGUI':
            try:
                sectionInSGUI = int(value)
            except ValueError as e:
                print('RaiseError, unexpected value! node: {}'.format(name))
                raise

    # recurse
    children = node.getchildren()
    if children:
        for child in children:
            validate_XML(child)


def getOrganizeSceneGraphInfo(node, info_dict):

    name = node.get('nodeName')
    useInorganizeSGUI = True if node.get('useInorganizeSGUI').upper() == 'TRUE' else False
    sectionInSGUI = int(node.get('sectionInSGUI'))

    # get info of placement inte organize scenegraph UI
    if useInorganizeSGUI:

        sectionInSGUI_dict = info_dict.get('sectionInSGUI')

        if sectionInSGUI not in sectionInSGUI_dict:
            sectionInSGUI_dict[sectionInSGUI] = []

        sectionInSGUI_dict[sectionInSGUI].append(name)

    # recurse
    children = node.getchildren()
    if children:
        for child in children:
            getOrganizeSceneGraphInfo(child, info_dict)

    return info_dict


tree = ET.parse('nodeWithAttrib.xml')
validate_XML(tree.getroot())

info_dict = {'sectionInSGUI':{}, 'other':[]}
getOrganizeSceneGraphInfo(tree.getroot(), info_dict)
pprint.pprint(info_dict)