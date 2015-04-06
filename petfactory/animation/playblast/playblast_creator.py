import pymel.core as pm
import maya.mel as mel
import petfactory.util.verify as pet_verify

def get_current_camera():
    
    try:
        camera_unicode = pm.modelPanel(pm.getPanel(wf=True), q=True, cam=True)
        return pet_verify.to_pynode(camera_unicode)

    except RuntimeError as e:
        print('Could not get the camera', e)
        return None
        

def get_time():
    
    return pm.currentTime(query=True)

           
def do_playblast(current_camera, start_time, end_time, file_name, width, height):
        
    if not pet_verify.verify_pynode(current_camera, pm.nodetypes.Camera):
        pm.warning('Not a valid camera!')
        return None
    
    # look through the camera
    mel.eval('lookThroughModelPanel {0} modelPanel4'.format(current_camera)) 
    
    # do the playblast 
    pm.playblast(startTime=start_time, endTime=end_time, format="avfoundation", viewer=False, compression="H.264", widthHeight=(width,height), showOrnaments=True, filename='movies/{0}'.format(file_name), offScreen=True)
    




#current_camera = get_current_camera()
'''
cam_1 = pm.PyNode('camera1')
cam_2 = pm.PyNode('camera2')

test(cam_1, start_time=40, end_time=80, file_name='cam 1', width=960, height=540)
test(cam_2, start_time=40, end_time=80, file_name='cam 2', width=1280, height=720)
'''