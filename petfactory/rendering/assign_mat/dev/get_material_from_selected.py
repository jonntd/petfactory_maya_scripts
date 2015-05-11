
shape_list = pm.ls(dag=True, o=True, s=True, sl=True)
sg_list = pm.listConnections(shape_list, type='shadingEngine')
mat_list = list(set(pm.ls(pm.listConnections(sg_list), materials=True)))
