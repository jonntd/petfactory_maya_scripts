import maya.cmds as cmds


def setNodeState(switchName, state):
    
    if not cmds.objExists(switchName):
        print('No object matches name: {}'.format(switchName))
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

setNodeState(switchName, state)