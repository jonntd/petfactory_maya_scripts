import re

pattern = re.compile(r'[\s.-]+')
name = 'asdas-dsfsdf  .. fsd'
print(re.sub(pattern, '_', name))