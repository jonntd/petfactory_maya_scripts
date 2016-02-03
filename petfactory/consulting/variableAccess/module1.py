#import petfactory.consulting.sharedStuff
#reload(petfactory.consulting.sharedStuff)

import sharedStuff
reload(sharedStuff)

def sayHello():
    #print petfactory.consulting.sharedStuff.a
    print sharedStuff.pet.sayHello()

def chaneName(newName):
    #print petfactory.consulting.sharedStuff.a
    sharedStuff.pet.setName(newName)