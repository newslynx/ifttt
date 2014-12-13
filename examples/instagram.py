from ifttt import ifthis

pattern = {
	"caption": "{{Caption}}",
	"url": "{{Url}}",
	"source_url": "{{SourceUrl}}",
	"username": "{{Username}}",
	"published": "{{CreatedAt}}"
}

@ifthis('instagram', pattern=pattern)
def instagram(msg):
	print msg

if __name__ == '__main__':
	instagram()


