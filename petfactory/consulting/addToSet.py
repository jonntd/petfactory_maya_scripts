def createSwitchSet():
    
    pm.select(deselect=True, clear=True)
    
    geometrySwitchSet = pm.sets(name='G__SWITCH_SET')
    materialSwitchSet = pm.sets(name='T__SWITCH_SET')
    
    return {'G__SWITCH_SET':geometrySwitchSet, 'T__SWITCH_SET':materialSwitchSet}
    

def createChildSet(parentSet, name, nodeList):
    
    pm.select(deselect=True, clear=True)
    childSet = pm.sets(name=name)
    pm.sets(childSet, e=True, forceElement=nodeList)
    pm.sets(parentSet, e=True, forceElement=childSet)

    
    
sphereGeo = pm.polySphere(n='sphereGeo')[0]
cubeGeo = pm.polyCube(n='cubeGeo')[0]

mainSwitchSets = createSwitchSet()
geometrySwitchSet = mainSwitchSets.get('G__SWITCH_SET')
materialSwitchSet = mainSwitchSets.get('T__SWITCH_SET')

createChildSet(geometrySwitchSet, 'G__SPHERE', sphereGeo)
createChildSet(materialSwitchSet, 'T__SPHERE', [sphereGeo, cubeGeo])

