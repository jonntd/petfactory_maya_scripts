import pymel.core as pm


def create_shot_from_timerange(current_shot=None, camera=None):
    
    if camera is None:
        
        try:
            camera = pm.PyNode(pm.modelPanel(pm.getPanel(wf=True), q=True, cam=True))
    
        except RuntimeError as e:
            pm.warning('Make sure you are in a camera view!')
            return
        
    my_shot_name = 'shot_{0}'.format(camera.shortName())
    
    start_time = pm.playbackOptions(q=True, min=True)
    end_time = pm.playbackOptions(q=True, max=True)
        
    if current_shot is None:
        seq_start_time = start_time
        seq_end_time = end_time
        
    else:
        seq_start_time =  current_shot.getSequenceEndTime() + 1
        seq_end_time = seq_start_time + (end_time - start_time)
    
    shot = add_shot(start_time, end_time, seq_start_time, seq_end_time, camera, my_shot_name)
    return shot
    
    


shot = create_shot_from_timerange()
shot = create_shot_from_timerange(shot)
shot = create_shot_from_timerange(shot)










