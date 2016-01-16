import unittest
import sgUtil

class TestStringMethods(unittest.TestCase):

    def testCreateNode(self):
        node = sgUtil.Node(name='root', type=sgUtil.INT)
        self.assertEqual(node.name, 'root')
        return node

    def testAddChild(self):
        node = sgUtil.Node(name='root', type=sgUtil.INT)
        rootNode = self.testCreateNode()
        rootNode.addChild(node)
        self.assertEqual(node.parent, rootNode)
        
    def testAddChildren(self):
        parentNode = sgUtil.GroupNode(name='root', type=sgUtil.INT)
        for i in range(10):
            n = sgUtil.Node(name='node{}'.format(i), type=sgUtil.INT)
            parentNode.addChild(n)

        self.assertEqual(parentNode.numChildren, 10)
    
    def testGroupNodeType(self):
        intNode = sgUtil.GroupNode(name='root', type=sgUtil.INT)
        self.assertEqual(intNode.type, sgUtil.INT)

    def testGroupNodeTypeMiss(self):
        intNode = sgUtil.GroupNode(name='MEDIA', type=sgUtil.INT)
        self.assertNotEqual(intNode.type, sgUtil.EXT)

    def testSwitchNodeType(self):
        intNode = sgUtil.SwitchNode(name='MEDIA', type=sgUtil.INT)
        self.assertEqual(intNode.type, sgUtil.INT)

    def testSwitchNodeClass(self):
        node = sgUtil.SwitchNode(name='MEDIA', type=sgUtil.EXT)
        self.assertEqual(type(node), sgUtil.SwitchNode)

    def testGroupNodeClass(self):
        node = sgUtil.GroupNode(name='MEDIA', type=sgUtil.EXT)
        self.assertEqual(type(node), sgUtil.GroupNode)

if __name__ == '__main__':
    unittest.main()