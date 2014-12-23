import yaml
import os
import sys
f = open( os.path.join(sys.path[0],'..','conf.yaml') )  
conf = yaml.load(f)  
f.close() 

# print conf['ds']
# print conf['ds']['db1']
# print conf['ds']['db1']['url']
# print conf['ds']['db1']['username']
# print conf['ds']['db1']['password']
