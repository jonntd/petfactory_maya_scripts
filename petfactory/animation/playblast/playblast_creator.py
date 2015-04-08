import pymel.core as pm
import maya.mel as mel
import datetime
import os

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

           
def do_playblast(current_camera, file_name, start_time, end_time, dir_path, width, height):
        
    if not pet_verify.verify_pynode(current_camera, pm.nodetypes.Camera):
        pm.warning('Not a valid camera!')
        return None
    
    
    # look through the camera
    mel.eval('lookThroughModelPanel {0} modelPanel4'.format(current_camera)) 
    
    # do the playblast 
    pm.playblast(startTime=start_time, endTime=end_time, format="avfoundation", viewer=False, compression="H.264", widthHeight=(width,height), showOrnaments=True, filename='{0}/{1}'.format(dir_path, file_name), offScreen=True)
    
    print('Playblast created in directory:\n{0}'.format(dir_path))


def create_playblast_directory(root_path):
    
    time_string = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")
    dir_name = 'playblasts {0}'.format(time_string)

    dir_path = os.path.join(root_path, dir_name)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return dir_path

    else:
        print('Exists!')
        return None


'''
cam_1 = pm.PyNode('camera1')
cam_2 = pm.PyNode('camera2')

dir = create_playblast_directory()

if dir is not None:
    do_playblast(cam_1, start_time=40, end_time=80, dir_path=dir, width=960, height=540)
'''

#pm.playblast(startTime=1, endTime=40, format="avfoundation", viewer=False, compression="H.264", widthHeight=(960,540), showOrnaments=True, filename='/Users/johan/Desktop/playblasts 2015-04-06 23.01.59/{0}'.format(cam_1), offScreen=True)
