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

requiredAttrib = [ 'name',
                    'nodeType',
                    'prefix',
                    'sectionInSGUI']

def validateXML(node):

    name = node.get('name')
    if name == '':
        raise NameError('the node has no name!')

    # make sure that all the required attributes exist and validate their values
    attrbs = node.attrib
    for attrb, value in attrbs.iteritems():
        if not attrb in requiredAttrib:
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
            validateXML(child)


def getOrganizeSceneGraphInfo(xmlNode, infoDict):

    name = xmlNode.get('name') 
    nodeType = xmlNode.get('nodeType')
    prefix = xmlNode.get('prefix')
    sectionInSGUI = int(xmlNode.get('sectionInSGUI'))

    # get info of placement inte organize scenegraph UI
    if sectionInSGUI > 0:

        if sectionInSGUI not in infoDict:
            infoDict[sectionInSGUI] = []

        infoDict[sectionInSGUI].append(buildVredName(name, nodeType, prefix))

    # recurse
    children = xmlNode.getchildren()
    if children:
        for child in children:
            getOrganizeSceneGraphInfo(child, infoDict)

    return infoDict

def buildVredName(name, nodeType, prefix):

    switchPrefix = 'G__' if nodeType.upper() == 'SWITCH' else ''
    prefix = prefix if prefix == '' else '{}_'.format(prefix)  
    nodeName = '{}{}{}'.format(switchPrefix, prefix, name)
    return nodeName

def mayaXML(xmlNode, parent=None, depth=-1):

    name = xmlNode.get('name') 
    nodeType = xmlNode.get('nodeType')
    prefix = xmlNode.get('prefix')
    nodeName = buildVredName(name, nodeType, prefix)

    print('{}{}'.format(depth*'\t', nodeName))

    mayaNode = pm.group(em=True, name=nodeName)

    if parent:
        pm.parent(mayaNode, parent)

    depth += 1

    children = xmlNode.getchildren()
    if children:
        for child in children:
            mayaXML(child, mayaNode, depth)


def createVredScenegraph(XMLpath):

    tree = ET.parse(XMLpath)
    validateXML(tree.getroot())
    #mayaXML(tree.getroot())

def createOrganizeVredUI(XMLpath):

    tree = ET.parse(XMLpath)
    validateXML(tree.getroot())

    infoDict = {}
    getOrganizeSceneGraphInfo(tree.getroot(), infoDict)

    keys = infoDict.keys()
    keys.sort()

    for index, key in enumerate(keys):
        nameList = infoDict[key]
        if index > 0:
            print('--------')
        for name in nameList:
            print(name)


path = r'/Users/johan/Dev/maya/petfactory_maya_scripts/petfactory/scene/recursive_hierarchy/nodeWithAttrib.xml'

createVredScenegraph(path)

createOrganizeVredUI(path)

