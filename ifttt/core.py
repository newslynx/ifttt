from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import imaplib
import smtplib
import email
import re
import time
from functools import wraps
import json

import config
import util

class IfThis:

    def __init__(self, channel, **kw):
        """
        Login to an imap client, and set the schema 
        for an IfTTT plugin 

        A schema-file should be a json blob 
        that is used to format the input from 
        IfTTT. Try to be minimal here and instead 
        used content-extraction tools to standardize 
        and add metadata by accessing the url.

        A schema object shoul be a format like this 
        (for twitter, in this case):

            { 
                "user_name": "{{UserName}}", 
                "text": "{{Text}}", 
                "created_at": "{{CreatedAt}}", 
                "short_url": "{{LinkToTweet}}" 
            }

        """
        self.channel = channel
        self.pattern = kw.get('pattern', None)
        self.username = kw.get('username', config.IFTTT_USERNAME)
        self.password = kw.get('password', config.IFTTT_PASSWORD)
        self.server = kw.get('server', config.IFTTT_IMAP_SERVER)
        
        self.refresh = kw.get('refresh', 10)
        self.cache_size = kw.get('cache_size', 100)
        self.cache = []

    def main(self, msg):
        """
        Custom callback for ifttt email message.
        """
        raise NotImplementedError('IfThis requires a custom `main` method.')

    def run(self):
        """
        Listen to an imap inbox for new messages
        from ifttt and pass parsed body to `on_message`
        """

        while True:
            
            # login and check inbox 
            self._login()
            for msg in self._check_inbox():
                if msg and msg['id'] not in self.cache:
                    self._cache_control(msg)
                    self.main(msg)

            time.sleep(self.refresh/2)
            self._logout()
            time.sleep(self.refresh/2)

    def _login(self):
        self.client = imaplib.IMAP4_SSL(self.server)
        self.client.login(self.username, self.password)
        self.client.select('inbox')

    def _logout(self):
        self.client.logout()

    def _query(self):
        if not self.channel:
            return "ALL"
        else:
            return '(SUBJECT "{}")'.format(self.channel)

    def _check_inbox(self):
        
        msgs = []
        result, data = self.client.search(None, self._query())
        ids = data[0]
        id_list = ids.split()

        if len(id_list):
            for i, id in enumerate(list(reversed(id_list))):
                if i < self.cache_size:
                    result, msg = self.client.fetch(id, "(RFC822)")
                    raw = msg[0][1]
                    yield self._parse(raw)

        else:
            yield None 

    def _parse(self, raw):
        """
        pre process raw message
        """

        # clean the keys 
        clean = {}

        msg = email.message_from_string(raw)

        # get the content 
        raw, body = self._parse_body(msg)

        # simplify
        clean  = {}
        clean['id'] = msg['Message-Id'].replace('<', '').replace('>', '')
        clean['from'] = msg['from'].replace('<', '').replace('>', '')
        clean['to'] = msg['to'].strip()
        clean['subject'] = msg['subject'].strip()
        clean['body'] = body
        
        return clean

    def _parse_body(self, msg):
        
        # get the msg
        parts = msg.get_payload()
        msg = parts[-1]
        raw = msg.get_payload().strip()

        if isinstance(self.pattern, dict):
            
            body = json.loads(raw)
            
            for k in self.pattern.keys():
                if k not in body:
                    raise ValueError('Body missing required key {}'.format(k))

        elif is_instance(obj, re._pattern_type):

            m = self.pattern.search(raw)
            if not m:
                raise ValueError('Bad Regex')

            body = m.groupdict()

        else:

            raise NotImplementedError('IfThis requires a pattern (regex / schemamap)')

        
        return raw, body

    def _cache_control(self, msg):
        self.cache.append(msg['id'])
        if len(list(self.cache)) > self.cache_size:
            self.cache = self.cache[-(self.cache_size-1)]


def ifthis(channel, **dkwargs):
  """
  listen to custom source and emit messages 
  to an email inbox with a custom channel as the subject 
  """
  # wrapper
  def wrapper(f):

    @wraps(f)
    def wrapped_func(*args, **kw):
        
        class _T(IfThis):
            def __init__(self):
                IfThis.__init__(self, channel, **dkwargs)
            
            def main(self, message):
                f(message)

        return _T().run()

    return wrapped_func

  return wrapper


class ThenThat:
    """
    Route messages back into IFTTT via email
    """
    def __init__(self, channel, **kw):

        self.channel = channel
        self.to = kw.get('to', config.IFTTT_USERNAME)
        self.username = kw.get('username', config.IFTTT_USERNAME)
        self.password = kw.get('password', config.IFTTT_PASSWORD)
        self.server = kw.get('server', config.IFTTT_SMTP_SERVER)
        self.port = kw.get('port', config.IFTTT_SMTP_PORT)
        self.refresh = kw.get('refresh', 10)


    def main(self):
        """
        Main loop.
        """
        raise NotImplementedError('ThenThat requires a custom `main` method.')

    def run(self):
        """
        Main publishing loop.
        """
        self._login()
        for msg in self.main():
            if msg:
                self._send(msg)
            time.sleep(self.refresh)
        self._logout()

    def _login(self):
        """
        Login to SMTP server.
        """

        self.client = smtplib.SMTP(self.server, self.port)
        self.client.ehlo()
        self.client.starttls()
        self.client.login(self.username, self.password)

    def _logout(self):
        """
        Logout of SMTP server.
        """
        self.client.close()

    def _send(self, msg):
        """
        Send a message
        """
        msg = self._format_msg(msg)
        self.client.sendmail(self.username, self.to,msg)

    def _format_msg(self, body):
        """
        Format message.
        """

        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = self.channel
        msg['From'] = self.to
        msg['To'] = self.to
        
        # add timestamp / serialize
        body['timestamp'] = util.now()
        msg_string = json.dumps(body)
        
        # build up message body
        body = MIMEMultipart('alternative')
        part1 = MIMEText(msg_string, 'plain')
        part2 = MIMEText(msg_string , 'html')
        body.attach(part1)
        body.attach(part2)
        msg.attach(body)  

        # convert to string  
        return msg.as_string()


def thenthat(channel, **dkwargs):
  """
  listen to an email subject and emit messages 
  to a callback 
  """
  # wrapper
  def wrapper(f):

    @wraps(f)
    def wrapped_func(*args, **kw):
        
        class _T(ThenThat):
            
            def __init__(self):
                ThenThat.__init__(self, channel, **dkwargs)
            
            def main(self):
                f()

        return _T().run()

    return wrapped_func

  return wrapper

def now():
  dt = datetime.utcnow()
  dt = t.replace(tzinfo=pytz.utc)
  return int(dt.strftime('%s'))




