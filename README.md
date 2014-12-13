# ifttt
helpers for connecting [IFTTT](http://ifttt.com) with any other service via `email`

## what?

[IFTTT](http://ifttt.com) provides an interface to an amazing number of services, but since they
lack their own API and have a closed submission process, it's difficult to integrate it into
your applications.  

By creating a set of transformations for routing IFTTT channels to email,
we can pass structured data to custom callback functions – `ifthis` – or listen to other services and send emails which can be processed by IFTTT - `thenthat`.

## installation / dependencies 

```
pip install ifttt
```

Our implementation is written and native python 2.7 and has no dependencies.

## examples

###  If This ... 

```python 
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


# when we run this script it will listen indefinitely for new messages
# on this routing key
if __name__=="__main__":
	twitter()

```

### Channels  (In Progress!, Please Contributes)
```python
from ifttt import channels
from pprint import pprint

pprint(channels) ## a simple hash of channel => pattern
```

### configuration

export these environmental variables:

```bash
export IFTTT_USERNAME='username@domain.com'
export IFTTT_PASSWORD='password'
export IFTTT_IMAP_SERVER='mail.domain.com'
export IFTTT_IMAP_PORT=993
export IFTTT_SMTP_SERVER='mail.domain.com'
export IFTTT_SMTP_PORT=587
```

## TODO
- [ ] Delete Messages 
- [ ] Create [comprehensive libraries of channels](ifttt/lib.py)
- [ ] Persistent caching so duplicates arent emitted.
