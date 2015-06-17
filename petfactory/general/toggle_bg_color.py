import pymel.core as pm

ro, go, bo = pm.displayRGBColor('background', q=True)

white = 1.0
grey = .6

if ro != 1.0:
    pm.displayRGBColor('background', white, white, white)
    
else:
    pm.displayRGBColor('background', grey, grey, grey)