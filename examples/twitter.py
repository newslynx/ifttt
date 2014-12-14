from ifttt import ifthat

@ifthat('twitter', pattern = "{{UserName}}|||||{{LinkToTweet}}|||||{{Text}}|||||")
def twitter(msg):
	import os 
	os.system('tweet from {text}'.format(**msg['body']))

if __name__ == '__main__':
	for msg in twitter():
		print msg


