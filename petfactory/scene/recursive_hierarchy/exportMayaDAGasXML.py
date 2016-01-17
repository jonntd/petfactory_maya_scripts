from PySide import QtCore, QtGui
import xml.etree.ElementTree as ET
import xml.dom.minidom

def recurseHierarchy(mayaNode, xmlParent):
    
    xmlNode = ET.Element('node')
    xmlNode.set('name', mayaNode.name())
    xmlNode.set('nodeType', 'group')
    xmlNode.set('prefix', 'INT')
    xmlNode.set('sectionInSGUI', '1')
    xmlParent.append(xmlNode)
    
    numChildren = mayaNode.numChildren()
    print(numChildren)
    if numChildren > 0:
        
        children = mayaNode.getChildren()
        for child in children:
            print(child)
            recurseHierarchy(child, xmlNode)

def exportHierarchyXML():
    
    sel = pm.ls(sl=True)
    if len(sel) < 1:
        print('Nothing is selected!')
        return
        
    mayaNode = sel[0]
    xmlRoot = ET.Element('root')
    recurseHierarchy(mayaNode, xmlRoot)
    xmlString = ET.tostring(xmlRoot)
    miniDomXml = xml.dom.minidom.parseString(xmlString)
    prettyXML = miniDomXml.toprettyxml()
    
    fname, _ = QtGui.QFileDialog.getSaveFileName(caption='Save XML', directory='/home', filter='*.xml')

    if(fname):
        f = open(fname,'w')
        f.write(prettyXML)
        f.close()
    
exportHierarchyXML()