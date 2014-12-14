import gevent
from gevent.pool import Pool

# patch everything except for thread.
import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()
gevent.monkey.patch_os()
gevent.monkey.patch_time()
gevent.monkey.patch_select()
gevent.monkey.patch_subprocess()

# normal imports
import re
import time
from functools import wraps
import json
from datetime import datetime
import pytz
import random

# email imports
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import imaplib
import smtplib
import email

# config
import config

# camel case => underscore
_re_cml1 = re.compile('(.)([A-Z][a-z]+)')
_re_cml2 = re.compile('([a-z0-9])([A-Z])')

# named regex pattern/delimiter formatter
_re = r"(?P<{}>.+){}"

# named regex pattern with delimiter
def _no_camel(s):
    # parse camel case
    s1 = _re_cml1.sub(r'\1_\2', s)
    return _re_cml2.sub( r'\1_\2', s1).lower()

def _get_required(pattern, delim):
    # extract and clean keys
    return [
        _no_camel(f.strip().replace('{', '').replace('}', ''))
            for f in pattern.strip().split(delim) 
                if f.strip() != ""
        ]

def linter(pattern, delim=config.IFTTT_DELIM):
    """
    Take in a raw IFTTT pattern that looks like this:
    
        {{Url}}|||||
        {{SourceUrl}}||||| 
        {{Caption}}|||||
        {{CreatedAt}}|||||
        {{EmbedCode}}|||||

    And format into a tuple of (regex, required_keys),
    something like this:

        (   
            # regex (will be pre-compiled!)
            r'^(?P<url>.+)\|\|\|\|\|(?P<source_url>.+)\|\|\|\|\|(?P<caption>.+)\|\|\|\|\|(?P<created_at>.+)\|\|\|\|\|(?P<embed_code>.+)\|\|\|\|\|$', 
            
            # required keys
            ['url', 'source_url', 'caption', 'created_at', 'embed_code'], 
        )

    """
    #clean whitespace
    pattern = re.sub('\s+', '', pattern)

    # get requires
    requires = _get_required(pattern, delim.replace('\|', '|'))

    # format regex
    regex_items = [_re.format(k, delim) for k in requires]
    regex_string = "^{}$".format("".join(regex_items))
    regex = re.compile(regex_string, re.VERBOSE | re.IGNORECASE)
    return pattern, regex, requires


class IfThat:

    def __init__(self, subject, **kw):
        """
        """
        self.subject = subject

        # lint pattern.
        self.pattern, self.regex, self.requires = \
            linter(kw.get('pattern'))

        self.username = kw.get('username', config.IFTTT_USERNAME)
        self.password = kw.get('password', config.IFTTT_PASSWORD)
        self.server = kw.get('server', config.IFTTT_SERVER)
        self.port = kw.get('port', config.IFTTT_PORT)
        self.refresh = kw.get('refresh', 120)
        self.random_factor = kw.get('random_factor', 0.2)
        self.cache_size = kw.get('cache_size', 100)
        self.pool = Pool(kw.get('num_workers', 5))
        self.cache = []
        

    def thenthis(self, msg):
        """
        Custom callback for ifttt email message.
        return single, modified message, or just 
        True if output is not required
        """
        raise NotImplementedError('IfThis requires a custom `thenthis` method.')

    
    def run(self):
        """
        Main loop.
        Listen to an imap inbox for new messages
        from ifttt and pass parsed body to `thenthis`
        """
        
        def _thenthis(msg):
            """
            Check cache on runtime
            """
            if msg and msg['id'] not in self.cache:
                self._update_cache(msg)

                # yield message
                return self.thenthis(msg)

        # endless loop
        while True:

            # login and check inbox, yield new messages
            self._login()
            for msg in self.pool.imap_unordered(_thenthis, self._check_inbox()):
                if msg:
                    yield msg

            # pause, login, pause with noise, iterate (blocking!)
            time.sleep(self.refresh * self._noise() / 2)
            self._logout()
            time.sleep(self.refresh * self._noise() / 2)

    def _login(self):
        """
        Login to check new mail.
        """
        self.client = imaplib.IMAP4_SSL(self.server)
        self.client.login(self.username, self.password)
        self.client.select('inbox')

    def _logout(self):
        """
        Logout to refresh.
        """
        self.client.logout()

    def _gen_query(self):
        """
        Format the query from the subject.
        """
        if not self.subject:
            return "ALL"
        else:
            return '(SUBJECT "{}")'.format(self.subject)

    def _check_inbox(self):
        """
        Poll the inbox for new messages,
        parse, and yield.

        TODO: push them to a queue ()
        """
        msgs = []
        result, data = self.client.search(None, self._gen_query())
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
        # parse the message
        msg = email.message_from_string(raw)

        # normalize
        clean = {}
        clean['id'] = msg['Message-Id'].replace('<', '').replace('>', '')
        clean['from'] = msg['from'].replace('<', '').replace('>', '')
        clean['to'] = msg['to'].replace('<', '').replace('>', '').strip()
        clean['subject'] = msg['subject'].strip()
        clean['body'] = self._parse_body(msg)
        clean['timestamp'] = self._now()

        # return
        return clean

    def _check_required(self, body):
        """
        check body post regex for programattically 
        determined fields
        """
        missing = []
        if len(self.requires):
            for k in self.requires:
                if k not in body:
                    missing.append(k)
        
        if len(missing):
            raise ValueError('Body missing required keys: {}'.format(",\n".join(k)))

    def _parse_body(self, msg):
        """
        parse body via regex.
        """
        # get the msg
        parts = msg.get_payload()
        msg = parts[-1]
        raw = msg.get_payload().strip()

        if isinstance(self.regex, re._pattern_type):
            m = self.regex.search(raw)
            if not m:
                raise ValueError('Bad regex!')
            body = m.groupdict()
            self._check_required(body)
            return body

        else:
            raise NotImplementedError('Regex must be compiled!')

    def _update_cache(self, msg):
        """
        Update the in-memory cache.
        """
        self.cache.append(msg['id'])
        if len(list(self.cache)) > self.cache_size:
            self.cache = self.cache[-(self.cache_size - 1)]

    def _now(self):
        """
        Current UTC timestamp
        """
        dt = datetime.utcnow()
        dt = dt.replace(tzinfo=pytz.utc)
        return int(dt.strftime('%s'))

    def _noise(self):
        """
        Some random noise in sleep intervals
        """
        f = int(10.0 * self.random_factor)
        return random.choice([x/100. for x in range(100-f, 100+f, 1)])


