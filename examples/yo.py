from ifttt import ifthis
from ifttt import util


pattern ={
	"published": "{{ReceivedAt}}",
	"from": "{{From}}" 
}

@ifthis('yo', pattern=pattern)
def yo(msg):
	import os 
	print msg
	os.system('say "YO FROM {from}"'.format(**msg['body']))

if __name__ == '__main__':
	yo()


