import maya.cmds as cmds


def setNodeState(switchName, state):
    
    if not cmds.objExists(switchName):
        print('{} -> No object matches this switch name'.format(switchName))
        return
    
    childList = cmds.listRelatives(switchName, children=True)
    
    if len(childList) > 0:
        
        if state not in childList:
            print('{} -> No object matches state named: {}'.format(switchName, state))
            return
        
        try:
            cmds.setAttr('{}.v'.format(state), vis)
            
        except RuntimeError as e:
            print('{} -> Could not set state "{}" -> {}'.format(switchName, state, e))
            return


switchName = 'G__ROOF'
state = 'ROOF_SUNROOF'
vis = True

#setNodeState(switchName, state)


def setMaterialState(switchName, state):
    
    # validate switchName
    if not cmds.objExists(switchName):
        print('{} -> No object matches this switch name'.format(switchName))
        return
        
    if not cmds.objectType(switchName, isType='objectSet'):
        print('{} -> is not a set'.format(switchName))
        return
        
    memberList = cmds.sets(switchName, q=True)
    
    if len(memberList) < 1:
        print('{} -> the set has no members"'.format(switchName))
        return
    
    
    # validate state
    if not cmds.objExists(state):
        print('{} -> No object matches the state "{}"'.format(switchName, state))
        return
    
    if not cmds.objectType(state, isAType='shadingDependNode'):
        print('{} -> The current state is not a shadingDependNode "{}"'.format(switchName, state))
        return
         
    sgList = cmds.listConnections(state, type='shadingEngine')     
    
    if not sgList:
        print('{} -> Could not get the shadingGroup of state "{}"'.format(switchName, state))
        return
        
    if len(sgList) < 1:
        print('{} -> The material has no ShadingGroup "{}"'.format(switchName, state))
        return
      
    cmds.sets(memberList, edit=True, forceElement=sgList[0])
            
        
    
switchName = 'T__TEST'
state = 'BLUE'

setMaterialState(switchName, state)