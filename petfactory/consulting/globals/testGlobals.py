
def test():

	mainWindow = __builtins__.get('vrMainWindow')
	
	if mainWindow is not None:
		print('main window was not none! {}'.format(mainWindow))
		return mainWindow
	else:
		print('main window was not set!')
		return None
