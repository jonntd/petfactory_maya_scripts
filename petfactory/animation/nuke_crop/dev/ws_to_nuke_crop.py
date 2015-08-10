import pymel.core as pm
import pprint
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
        
    
def ws_to_screen(sel_list, pos_list, z_offset, frame_start, frame_end):
    
    width = 1920
    height = 1080
    vec_z = pm.datatypes.VectorN(0, 0, z_offset, 1)
    vec_c = pm.datatypes.VectorN(0, 0, 0, 1)
    
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
    vec_list = [[] for x in sel_list]
    center_list = [[] for x in sel_list]
    z_offset_list = [[] for x in sel_list]
    
    # step through the timeline
    for frame in range(frame_start, frame_end+1):
        
        pm.currentTime(frame, update=True, edit=True)
        
        for index, sel in enumerate(sel_list):
            
            m = sel_list[index].getMatrix(ws=True)
            # mult the vec from the pos_lsi with the matrix of each object, slice the first 3 vec (skip thw w component)
            crop_vec_list = [(v*m)[:3] for v in pos_list]
        
            p_list = []
            for vec in crop_vec_list:
                
                # VISUAL DEBUG
                #sp = pm.polySphere(r=.2, ch=False)[0]
                #sp.translate.set((vec[0], vec[1], vec[2]))
                p_list.append(WorldPositionToImageCoordinate(cameraName=current_cam, imageXRes=width, imageYRes=height, worldX=vec[0], worldY=vec[1], worldZ=vec[2]))
                
            vec_list[index].append(p_list)
                        
            cm = (vec_c*m)[:3]
            zm = (vec_z*m)[:3]
            
            center_list[index].append(WorldPositionToImageCoordinate(cameraName=current_cam, imageXRes=width, imageYRes=height, worldX=cm[0], worldY=cm[1], worldZ=cm[2]))
            z_offset_list[index].append(WorldPositionToImageCoordinate(cameraName=current_cam, imageXRes=width, imageYRes=height, worldX=zm[0], worldY=zm[1], worldZ=zm[2]))
        
    # reset the time indicator
    pm.currentTime(curr_time, update=True, edit=True)
    
    for index, sel in enumerate(sel_list):
        
        node = {}
        node['name'] = sel.shortName()
        node['verts'] = vec_list[index]
        node['center'] = center_list[index]
        node['z_offset'] = z_offset_list[index]
        
        node_list.append(node)
        
    
    return ret_dict
    


def get_curve_string(an_attr_list, frame_start):
    
    s = '{ curve '
    
    for index, val in enumerate(an_attr_list): s += 'x{0} {1} '.format(frame_start+index, val)
    
    s += '}'
    
    return s
    

def build_nuke_pasteboard(x, y, r, t, name, vol_pos_x, vol_pos_y, frame_start, index):

    s = 'Crop {\n'
    s += '\tinputs 0'
    s += '\txpos {0}'.format(index * 100)
    s += '\typos {0}'.format(0)
    s += '\tname {0}'.format(name)
    s += '\tbox {\n'
    s += '\t\t{0}\n'.format(get_curve_string(x, frame_start))
    s += '\t\t{0}\n'.format(get_curve_string(y, frame_start))
    s += '\t\t{0}\n'.format(get_curve_string(r, frame_start))
    s += '\t\t{0}\n'.format(get_curve_string(t, frame_start))
    s+= '\t}\n'
    s+= '}\n'

    s += 'VolumeRays {\n'
    #s += '\tinputs 0'
    s += '\txpos {0}'.format(index * 100)
    s += '\typos {0}'.format(75)
    #s += '\tname {0}'.format(name)
    s += '\tvol_pos {\n'
    s += '\t\t{0}\n'.format(get_curve_string(vol_pos_x, frame_start))
    s += '\t\t{0}\n'.format(get_curve_string(vol_pos_y, frame_start))
    s+= '\t}\n'
    s+= '}\n'
    
    s+= 'set a [stack 0]\n'
    
    if index == 0:
        s += 'Dot {\n'
        #s += '\tinputs 0'
        s += '\txpos {0}'.format(35)
        s += '\typos {0}'.format(163)
        s+= '}\n'
        
        s+= 'set b [stack 0]\n'
        
        return s
    
    s += 'push $a\n'
    s += 'push $b\n'
    
    s += 'Merge2 {\n'
    s += '\tinputs 2'
    s += '\toperation plus'
    s += '\txpos {0}'.format(index * 100)
    s += '\typos {0}'.format(160)
    s+= '}\n'
    
    s+= 'set b [stack 0]\n'
    
    
    return s
    
    
       
def get_nuke_crop(sel_list, pos_list, frame_start, frame_end):
    
    z_offset = 3
    node_dict = ws_to_screen(sel_list, pos_list, z_offset, frame_start, frame_end)
    node_dict_list = node_dict.get('node_list')
    
    frame_start = node_dict.get('frame_start')
    
    #pprint.pprint(node_dict_list)
    
    offset = 0
    crop_list = []
    cmd_string = ''
    
    for index, node_dict in enumerate(node_dict_list):
        
        vert_list = node_dict.get('verts')
        z_offset_list = node_dict.get('z_offset')
        name = node_dict.get('name')
        
        
        x = []
        y = []
        r = []
        t = []
        vol_pos_x, vol_pos_y = zip(*z_offset_list)
            
        for vert in vert_list:

            px, py = zip(*vert)
            x.append(min(px)-offset)
            y.append(min(py)-offset)
            r.append(max(px)+offset)
            t.append(max(py)+offset)

                
        cmd_string += build_nuke_pasteboard(x, y, r, t, name, vol_pos_x, vol_pos_y, frame_start, index)

            
    os.system("echo {0} | pbcopy".format('\'' + cmd_string + '\''))
        
        

        
##################################




x_pos = 1
x_neg = -1
y_pos = 1
y_neg = -1

# declare once
vec_list = [    pm.datatypes.VectorN(x_pos, y_pos, 0, 1),
                pm.datatypes.VectorN(x_neg ,y_pos, 0, 1),
                pm.datatypes.VectorN(x_neg ,y_neg, 0, 1),
                pm.datatypes.VectorN(x_pos ,y_neg, 0, 1)]

#loc1 = pm.PyNode('|locator1')
#loc2 = pm.PyNode('|locator2')
sel_list = pm.ls(sl=True)


get_nuke_crop(sel_list=sel_list, pos_list=vec_list, frame_start=1, frame_end=1)
