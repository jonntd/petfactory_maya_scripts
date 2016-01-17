import xml.etree.ElementTree as ET


parent = ET.Element('node')
ip = ET.SubElement(parent, 'node', attrib={'name':'CAR', 'nodeType':'group', 'prefix':'', 'sectionInSGUI':'0'})
ET.dump(parent)

#def saveXml(parent):
	#node = ET.SubElement(parent, 'node', attrib={'name':'CAR', 'nodeType':'group', 'prefix':'', 'sectionInSGUI':'0'})


#ET.dump(root)