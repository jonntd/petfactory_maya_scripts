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
        
    
def ws_to_screen(vec_list, sel_list, frame_start, frame_end):
    
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
    
    #print(sel_list[0].shortName())
    
    ret_list = [[] for x in sel_list]
    

    # step through the timeline
    for frame in range(frame_start, frame_end+1):
        
        pm.currentTime(frame, update=True, edit=True)
        
        for index, sel in enumerate(sel_list):
            
            m = sel_list[index].getMatrix(ws=True)
            crop_vec_list = [(v*m)[:3] for v in vec_list]
        
            p_list = []
            for vec in crop_vec_list:
                
                # VISUAL DEBUG
                #sp = pm.polySphere(r=.2, ch=False)[0]
                #sp.translate.set((vec[0], vec[1], vec[2]))
                p_list.append(WorldPositionToImageCoordinate(cameraName=current_cam, imageXRes=width, imageYRes=height, worldX=vec[0], worldY=vec[1], worldZ=vec[2]))
                
            
            ret_list[index].append(p_list)   
        
    # reset the time indicator
    pm.currentTime(curr_time, update=True, edit=True)
    
    return ret_list
    


def get_curve_string(an_attr_list):
    
    s = '{ curve '
    
    for index, val in enumerate(an_attr_list): s += 'x{0} {1} '.format(index, val)
    
    s += '}'
    
    return s
    

def get_node(x, y, r, t):

    s = 'Crop {\n'
    s += '\tinputs 0'
    s += '\tbox {\n'
    s += '\t\t{0}\n'.format(get_curve_string(x))
    s += '\t\t{0}\n'.format(get_curve_string(y))
    s += '\t\t{0}\n'.format(get_curve_string(r))
    s += '\t\t{0}\n'.format(get_curve_string(t))
    s+= '\t}\n'
    s+= '}\n'

    return s
    
    
       
def get_nuke_crop(vec_list, sel_list, frame_start, frame_end):
    
    node_list = ws_to_screen(vec_list, sel_list, frame_start, frame_end)
    #pprint.pprint(node_list)
    
    offset = 10
    crop_list = []
    cmd_string = ''
    
    for p_list in node_list:
        
        x = []
        y = []
        r = []
        t = []
        for p in p_list:
            px, py = zip(*p)
            x.append(min(px)-offset)
            y.append(min(py)-offset)
            r.append(max(px)+offset)
            t.append(max(py)+offset)
            

        cmd_string += get_node(x, y, r, t)
        
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

loc1 = pm.PyNode('|locator1')
loc2 = pm.PyNode('|locator2')


get_nuke_crop(sel_list=[loc1, loc2], vec_list=vec_list, frame_start=0, frame_end=24)
