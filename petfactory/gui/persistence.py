from PySide import QtCore, QtGui
import json

def load_json(title, filter):
    
    file_name, selected_filter = QtGui.QFileDialog.getOpenFileName(None, title, None, filter)
    
    if file_name:

        data = None
        with open(file_name, 'r') as f:
            data = f.read()
        
        json_data = json.loads(data)
        
        return json_data
        
    
    else:
        return None



def save_json(save_dict, title, filter):
    
    file_name, selected_filter = QtGui.QFileDialog.getSaveFileName(None, title, None, filter)

    json_data = json.dumps(save_dict, indent=4)
    
    if file_name:
        with open(file_name, 'w') as f:
            f = open(file_name,'w')
            f.write(json_data)
            f.close()
            print('Data saved to file: {0}'.format(file_name))       

    else:
        print('Could not save file')