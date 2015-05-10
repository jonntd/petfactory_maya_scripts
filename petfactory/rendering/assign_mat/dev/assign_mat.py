ns = 'lookdev'
pm.importFile("/Users/johan/Desktop/pet_materials.mb", namespace=ns)

pm.namespace(force=True, mv=(':{0}'.format(ns), ':'))

# remove the namespace if it exists
if pm.namespace(exists=ns):
    
    try:
        pm.namespace(rm=ns)
        
    except RuntimeError as e:
        pm.warning('Could not remove namespace ', e)


#pm.objExists('test_blinn_1')
