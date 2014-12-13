from ifttt import ifthis

pattern = pattern = { 
	"user_name": "{{UserName}}", 
	"published": "{{CreatedAt}}", 
	"short_url": "{{LinkToTweet}}",
	"text": "{{Text}}"
}

@ifthis('twitter', pattern=pattern)
def twitter(msg):
	import os 
	print msg
	os.system('say {text}'.format(**msg['body']))


if __name__ == '__main__':
	twitter()


