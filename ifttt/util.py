import re
from string import punctuation
from datetime import datetime
import pytz
import json
import sys

re_wht = re.compile('\s+')
punct = frozenset(punctuation)

# current unix utc timestamp

def now(dt=False):
	d = datetime.utcnow()
	d = d.replace(tzinfo=pytz.utc)
	if dt:
		return d
	else:
		return int(d.strftime('%s'))


def rm_punct(s):
	return "".join([c for c in s if c not in punct])


def slug(s, sep="_"):
	s = rm_punct(s.strip().lower())
	s = re_wht.sub(' ', s).strip()
	return s.replace(' ', sep)


def is_regex(obj):
	return is_instance(obj, re._pattern_type)


def stdin():
	"""
	Read from stdin, parse json, 
	yield objects
	"""
	while True:
		
		try:
			line = sys.stdin.readline()
			if line:
				if line.strip() != '':
					yield json.loads(line)
			else:
				break
		
		except KeyboardInterrupT:
			break


def stdout(obj):
	"""
	Write jsonlines to stdout
	"""
	sys.stdout.write(json.dumps(obj) + "\n")
