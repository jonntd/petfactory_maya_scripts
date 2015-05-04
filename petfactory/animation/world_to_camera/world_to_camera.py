import maya.OpenMaya as OpenMaya

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


#print WorldPositionToImageCoordinate('camera1', 1920, 1080, 0, 28.951, -100)

cam = pm.PyNode('camera1')
loc = pm.PyNode('locator1')

def get_screen_position(cam, loc, image_width=1920, image_height=1080):
    
    w_pos = loc.getTranslation(ws=True)

    return WorldPositionToImageCoordinate(cam, worldX=w_pos[0], worldY=w_pos[1], worldZ=w_pos[2], imageXRes=image_width, imageYRes=image_height)
    
    
print(get_screen_position(cam, loc))