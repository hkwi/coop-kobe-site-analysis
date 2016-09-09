# coding: UTF-8
import sys
import re
import sqlite3
from urllib.parse import urljoin, urlparse, parse_qsl, urlunparse

db = sqlite3.connect("coop.db")
db.row_factory = sqlite3.Row
cur = db.cursor()
for line in sys.stdin:
	p = urlparse(line.strip())
	try:
		cur.execute('''INSERT INTO prefix(netloc,path) VALUES(?,?)''',
			(p.netloc, p.path))
		db.commit()
	except:
		pass
	
	try:
		cur.execute('''INSERT INTO target(scheme,netloc,path,params,query) VALUES(?,?,?,?,?)''', p[:5])
		db.commit()
	except:
		pass
