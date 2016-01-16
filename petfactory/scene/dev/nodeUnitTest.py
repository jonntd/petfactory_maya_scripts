import unittest
import node

class TestStringMethods(unittest.TestCase):

    def create_node(self):
        node = Node(name='root')
        self.assertEqual(node.name, 'roor')

    #def test_less_than_10(self):
      #self.assertLess(myCount.return_less_then_10(), 10)

if __name__ == '__main__':
    unittest.main()