import petfactory.consulting.variableAccess.sharedStuff
reload(petfactory.consulting.variableAccess.sharedStuff)

class Pet(object):
    def __init__(self, name):
        self._name = name
        
    def sayHello(self):
        print 'hello from {}'.format(self._name)
        
    def setName(self, name):
        self._name = name
        print 'I was renamed to {}'.format(name)

        
pet = Pet('mike') 
pet.sayHello()


petfactory.consulting.variableAccess.sharedStuff.pet = pet

import petfactory.consulting.variableAccess.module1
reload(petfactory.consulting.variableAccess.module1)

petfactory.consulting.variableAccess.module1.sayHello()
petfactory.consulting.variableAccess.module1.chaneName('apa')