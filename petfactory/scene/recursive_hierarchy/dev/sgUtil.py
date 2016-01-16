INT = 'INT'
EXT = 'EXT'

class Node(object):

    def __init__(self, name, type):
        self._name = name
        self._type = type
        self._children = []
        self._parent = None

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def numChildren(self):
        return len(self._children)

    @property
    def nodeType(self):
        return self._nodeType

    @property
    def type(self):
        return self._type

    def addChild(self, child):
        self._children.append(child)
        child.setParent(self)

    def setParent(self, parent):
        self._parent = parent

class GroupNode(Node):

    def __init__(self, name, type):
        super(GroupNode, self).__init__(name, type)

class SwitchNode(Node):

    def __init__(self, name, type):
        super(SwitchNode, self).__init__(name, type)


