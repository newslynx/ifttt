from ifttt import ifthat

@ifthat('yo', pattern="{{ReceivedAt}}|||||{{From}}|||||")
def yo(msg):
	import os
	os.system('say yo from {from} &'.format(**msg['body']))
	return msg 
	
for msg in yo():
	print msg

if __name__ == '__main__':
	for msg in yo(): pass
		


