import pymel.core as pm
import maya.cmds as cmds
import maya.api.OpenMaya as om
# the old api
import maya.OpenMaya as OpenMaya

import petfactory.util.verify as pet_verify


def floatMMatrixToMMatrix_(fm):
    '''thanks to KOICHI TAMURA'''
    mat = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList ([
        fm(0,0),fm(0, 1),fm(0, 2),fm(0, 3),
        fm(1,0),fm(1, 1),fm(1, 2),fm(1, 3),
        fm(2,0),fm(2, 1),fm(2, 2),fm(2, 3),
        fm(3,0),fm(3, 1),fm(3, 2),fm(3, 3)], mat)
    return mat


def WorldPositionToImageCoordinate(cameraName, imageXRes, imageYRes, worldX, worldY, worldZ):
    '''thanks to KOICHI TAMURA'''
    p = OpenMaya.MPoint(worldX, worldY, worldZ)
    sl = OpenMaya.MSelectionList()
    sl.add(cameraName)
    dpathCameraShape=OpenMaya.MDagPath()
    sl.getDagPath(0, dpathCameraShape)
    dpathCameraShape.extendToShape()
    fnc = OpenMaya.MFnCamera(dpathCameraShape.node())
    mmatProjection = floatMMatrixToMMatrix_(fnc.projectionMatrix())
    mmatInvCamera = dpathCameraShape.inclusiveMatrix().inverse();
    projected = p * mmatInvCamera * mmatProjection
    imageX = (projected.x/projected.w / 2.0 + 0.5) * imageXRes
    imageY = (projected.y/projected.w / 2.0 + 0.5) * imageYRes
    return imageX, imageY


def build_world_to_camera_dict(sel_list, frame_start, frame_end):
    
    # first lets see if we can get the current camera
    try:
        camera_unicode = pm.modelPanel(pm.getPanel(wf=True), q=True, cam=True)
        current_cam = pet_verify.to_pynode(camera_unicode)
        print(current_cam)

    except RuntimeError as e:
        print('Could not get the camera', e)
        return None
        
        
        
    obj_list = []
    null_attr = ['x', 'y']
   
    # gather scene info
    info_dict = {}
    
    time_format_dict = {'game':15, 'film':24, 'pal':25, 'ntsc':30, 'show':48, 'palf':50, 'ntscf':60}
    time_unit = pm.currentUnit(q=True, time=True)
    linear_unit = pm.currentUnit(q=True, linear=True)
    angle_unit = pm.currentUnit(q=True, angle=True)
    width = pm.getAttr('defaultResolution.width')
    height = pm.getAttr('defaultResolution.height')
    
    info_dict['time_unit'] = time_unit
    info_dict['linear_unit'] = linear_unit
    info_dict['angle_unit'] = angle_unit
    info_dict['fps'] = time_format_dict.get(time_unit)
    info_dict['frame_start'] = frame_start
    info_dict['frame_end'] = frame_end
    info_dict['width'] = width
    info_dict['height'] = height
    info_dict['device_aspect_ratio'] = pm.getAttr('defaultResolution.deviceAspectRatio')
    info_dict['pixel_aspect'] = pm.getAttr('defaultResolution.pixelAspect')
    info_dict['maya_version'] = cmds.about(version=True)
    
    # the name to use as the key in the dict, shortest unique or just the node name
    cache_name = []
    null_list = []
    ret_dict = {"null":null_list, 'info':info_dict}
    
    # loop through all the selected objects.
    # if it is a camera we will store it in the camera dict, and use the cam_attr
    for sel in sel_list:
        
        # make sure the obj is a transform
        if not isinstance(pm.PyNode(sel), pm.nodetypes.Transform):
            #print('is a NOT {0}'.format(sel))
            continue
        else:
            #print('is a {0}'.format(sel))
            obj_list.append(sel)  
        
        attr_dict = {} # this is the dict that stores the nodes attrs
        
        # static attributes (that does not change over time)
        #attr_dict['rotation_order'] = [cmds.getAttr('{0}.rotateOrder'.format(sel))]
        
        #if use_shortest_unique_name: n = obj.shortName() # the shortest unique
        #else: n = obj.nodeName() # just the node name
        
        # get the shortest unique name and store in the cache name list.
        # is used as a key in the nu
        n = sel.shortName()
        cache_name.append(n) # store the node nall_list and cam_listsme in a list for later use

        
        null_list.append({n:attr_dict})
            
        # create the keys for the dict
        for x in null_attr:
            attr_dict[x] = []


    if len(obj_list) < 1:
        pm.warning('No valid objects were selected!')
        return None


    # start stepping through the timeline, gatering anim data
    for frame in range(frame_start, frame_end+1):
        
        # Index to be used to acces the correct dict in the cam and null_lists
        null_index = 0
        cam_index = 0 
        
        pm.currentTime(frame, update=True, edit=True)
            
         # The index (from the enumerator) will be used to access the node names   
        for index, obj in enumerate(obj_list):

            #matrix = om.MTransformationMatrix(om.MMatrix(pm.xform(obj, q=True, ws=True, matrix=True)))
            #translate = matrix.translation(1)
            
            w_pos = obj.getTranslation(ws=True)
            
            cam_x, cam_y = WorldPositionToImageCoordinate(current_cam, worldX=w_pos[0], worldY=w_pos[1], worldZ=w_pos[2], imageXRes=width, imageYRes=height)
            
            
            for attr in null_attr:
            
                if attr is 'x': null_list[null_index][cache_name[index]]['x'].append(cam_x)
                elif attr is 'y': null_list[null_index][cache_name[index]]['y'].append(cam_y)

                    
            null_index += 1            
                        
    return ret_dict