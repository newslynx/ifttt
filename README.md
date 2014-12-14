# ifttt (If That Then This)
`ifttt` is a simple package for connecting [IFTTT](http://ifttt.com) 
channels with your service via and email inbox.

## what?

[IFTTT](http://ifttt.com) provides an interface to an amazing number of services, but since they
lack their own API and have a closed submission process, it's difficult to integrate it into
your applications.  

By creating a set of transformations for routing IFTTT channels to email,
we can pass structured data to custom email-listener functions – `ifthat`
which can be routed to an arbitrary `thenthis` function that a user defines.

## installation

```
pip install ifttt
```

Our implementation is written and native python 2.7 and has no dependencies.

## examples

###  If That Then Say Tweet ...


Make an "IfThis" Twitter Recipe that has an "ThenThat" 
mail step (customize the address to match your configuration)


[![](examples/twitter.png)](https://ifttt.com/recipes/229283-if-twitter-then-data)


```python 
from ifttt import ifthat

@ifthat('twitter', pattern = "{{UserName}}|||||{{LinkToTweet}}|||||{{Text}}|||||")
def twitter(msg):
	import os 
	os.system('tweet from {text}'.format(**msg['body']))
	return msg

for msg in twitter():
	print msg
```

### If This Then Say YO


Make an "IfThis" Yo Recipe that has an "ThenThat" 
mail step (customize the address to match your configuration)


[![](examples/yo.png)](https://ifttt.com/recipes/229285-if-yo-then-data)



```python
from ifttt import ifthat

@ifthat('yo', pattern="{{ReceivedAt}}|||||{{From}}|||||")
def then_yo(msg):
	import os
	os.system('say yo from {from} &'.format(**msg['body']))
	return msg 
	
for msg in yo():
	print msg
```

## Configuration

You can pass more parameters into the decorator:

```python
from ifttt import ifthat

config = {
	subject='yo', 
	pattern="{{ReceivedAt}}|||||{{From}}|||||",
	username='username@example.com',
	password='123456',
	server='mail.example.com',
	port=993,
	cache_size=100, # how many message ids to keep track in the cache (non-persistent),
	num_workers=5, # how many workers for the processing queue.
	refresh=120 # how often to refresh the inbox
}
@ifthat(**config)
def then_yo(msg):
	import os
	os.system('say yo from {from} &'.format(**msg['body']))
	return msg 
	
for msg in yo():
	print msg
```

You can also simply inherit from the core class and  overwrite the `thenthis` method:

```python
from ifttt import IfThat

class Yo(IfThat):
	def __init__(self):
		IfThat.__init__(self,
			subject = 'yo', 
			pattern="{{ReceivedAt}}|||||{{From}}|||||",
			username='username@example.com',
			password='123456',
			server='mail.example.com',
			port=993,
			cache_size=100, # how many message ids to keep track in the cache (non-persistent),
			num_workers=5, # how many workers for the processing queue.
			refresh=120 # how often to refresh the inbox 
		)

	def thenthis(self, msg):
		import os
		os.system('say yo from {from} &'.format(**msg['body']))
		return msg

yo = Yo()
for msg in yo.listen():
	print msg
```

Alternatively, you can set these environmental variables:

```bash
export IFTTT_USERNAME='username@domain.com'
export IFTTT_PASSWORD='password'
export IFTTT_SERVER='mail.domain.com'
export IFTTT_PORT=993
```

## TODO
- [ ] Delete Messages
