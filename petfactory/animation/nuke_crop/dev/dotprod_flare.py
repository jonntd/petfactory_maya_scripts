import pymel.core as pm
import pprint
import maya.OpenMaya as OpenMaya
import petfactory.util.verify as pet_verify
import math
    

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
        
    
def ws_to_screen(sel_list, frame_start, frame_end):
    
    width = 1920
    height = 1080
    
    # first lets see if we can get the current camera
    try:
        camera_unicode = pm.modelPanel(pm.getPanel(wf=True), q=True, cam=True)
        current_cam = pet_verify.to_pynode(camera_unicode)

    except RuntimeError as e:
        print('Could not get the camera', e)
        return None
        
    
    curr_time = pm.currentTime(q=True)
    
    ret_dict = {}
    info_dict = {}
    ret_dict['info'] = info_dict
    node_list = []
    ret_dict['node_list'] = node_list
    ret_dict['frame_start'] = frame_start
    ret_dict['fps'] = 25


    # crete a list to store the pos for each object
    c_list = [[] for x in sel_list]
    dotprod_list = [[] for x in sel_list]
    
    # step through the timeline
    for frame in range(frame_start, frame_end+1):
        
        pm.currentTime(frame, update=True, edit=True)
        
        for index, sel in enumerate(sel_list):
            
            #m = sel_list[index].getMatrix(ws=True)
            pos = sel_list[index].getRotatePivot(space='world')
            c_list[index].append(WorldPositionToImageCoordinate(    cameraName=current_cam,
                                                                    imageXRes=width,
                                                                    imageYRes=height,
                                                                    worldX=pos[0],
                                                                    worldY=pos[1],
                                                                    worldZ=pos[2]))
            
            dotprod_list[index].append(math.sin(frame*.1)*2)

    # reset the time indicator
    pm.currentTime(curr_time, update=True, edit=True)
    
    for index, sel in enumerate(sel_list):
        
        node = {}
        node['name'] = sel.shortName()
        node['center'] = c_list[index]
        node['dotprod'] = dotprod_list[index]
        node_list.append(node)
        
    
    return ret_dict
    


def get_curve_string(an_attr_list, frame_start):
    
    s = '{ curve '
    
    for index, val in enumerate(an_attr_list): s += 'x{0} {1} '.format(frame_start+index, val)
    
    s += '}'
    
    return s
    

def build_nuke_pasteboard(x, y, dotprod, name, frame_start, index):

        
    s = 'Transform {\n'
    s += '\tinputs 0'
    s += '\txpos {0}'.format(index * 100)
    s += '\typos {0}'.format(0)
    s += '\tname {0}'.format(name)
    s += '\ttranslate {\n'
    s += '\t\t{0}\n'.format(get_curve_string(x, frame_start))
    s += '\t\t{0}\n'.format(get_curve_string(y, frame_start))
    s+= '\t}\n'
    s += '\tscale {\n'
    s += '\t\t{0}\n'.format(get_curve_string(dotprod, frame_start))
    s+= '\t}\n'
    s+= '}\n'


    
    
    return s
    
    
       
def get_nuke_crop(sel_list, frame_start, frame_end):
    
    node_dict = ws_to_screen(sel_list, frame_start, frame_end)
    node_dict_list = node_dict.get('node_list')    
    frame_start = node_dict.get('frame_start')
    
    pprint.pprint(node_dict_list)
    
    cmd_string = ''
    
    for index, node_dict in enumerate(node_dict_list):
        
        p_list = node_dict.get('center')
        name = node_dict.get('name')
        dotprod = node_dict.get('dotprod')

        x, y = zip(*p_list)
                
        cmd_string += build_nuke_pasteboard(x, y, dotprod, name, frame_start, index)

            
    os.system("echo {0} | pbcopy".format('\'' + cmd_string + '\''))
        
        

        

sel_list = pm.ls(sl=True)
get_nuke_crop(sel_list=sel_list, frame_start=1, frame_end=100)
