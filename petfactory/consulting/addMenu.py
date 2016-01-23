mainMenuName = 'MyMenu'

def open_dir(dir_name, absolute_path, *args):
    
    '''
    Open the specified dir specified by the dir_name param.
    If param absolute_path is true the dir_name will be used as an absolute path.
    '''

    if absolute_path:
        folder_path = dir_name

    else:
        proj_dir = cmds.workspace(q=True, fn=True)
        folder_path = os.path.join(proj_dir, dir_name)
    
    if not os.path.exists(folder_path):
        cmds.confirmDialog(t='Could not find directory', b=['OK'],m='The directory does not exist:\n {0}'.format(folder_path))
    
    else:
        # try to open the directory
        try:
            subprocess.check_call(['open', '--', folder_path])
        
        except:
            cmds.confirmDialog(t='Error', b=['OK'],m='Unable to open folder:\n{0}'.format(folder_path))


def addMenu():

    if cmds.menu(mainMenuName, exists=1):
        cmds.deleteUI(mainMenuName)

    # add to the main menu
    mainMenu = cmds.menu(mainMenuName, p='MayaWindow', to=1, aob=1, l=mainMenuName)
    
    # the quick open folder menu
    projectDirMenu = cmds.menuItem('projectDirMenu', p=mainMenu, bld=1, sm=1, to=1, l='Open Project Directory')
    cmds.menuItem('movies', parent=projectDirMenu, c=partial(open_dir, 'movies', False), label='movies')
    cmds.menuItem('sourceimages', parent=projectDirMenu, c=partial(open_dir, 'sourceimages', False), label='sourceimages')
    cmds.menuItem('images', parent=projectDirMenu, c=partial(open_dir, 'images', False), label='images')
    cmds.menuItem('scenes', parent=projectDirMenu, c=partial(open_dir, 'scenes', False), label='scenes')
    
    cmds.menuItem(p=mainMenu, d=1)
    
    cmds.menuItem('test', parent=mainMenu, c=test, label='Test')

def test(a):
    print(a, 12)

addMenu()