# coding: UTF-8

import re
import sqlite3
from urllib.parse import urljoin, urlparse
import selenium.webdriver
# XXX: javascript:void() も通過させられる crawler があるといい

db = sqlite3.connect("coop.db")
db.row_factory = sqlite3.Row
cur = db.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS target (
	idx INTEGER PRIMARY KEY AUTOINCREMENT,
	url VARCHAR(255),
	host VARCHAR(255),
	body TEXT
)''')
cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS uniq_url ON target(url)''')
cur.execute('''CREATE TABLE IF NOT EXISTS di(src INTEGER, dst INTEGER)''')
cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS uniq_di ON di(src,dst)''')

def path2idx(path):
	path = path.split("#")[0]
	cur.execute("SELECT idx FROM target WHERE url=?", (path,))
	r = cur.fetchone()
	if r:
		return r["idx"]
	
	cur.execute("INSERT INTO target(url,host) VALUES(?,?)", (path, urlparse(path).netloc))
	db.commit()
	cur.execute("SELECT idx FROM target WHERE url=?", (path,))
	return cur.fetchone()["idx"]

agent = selenium.webdriver.Firefox()



#for s in ["www.coop-kobe.net", "www.kobe.coop.or.jp", "ck.coop-kobe.net", "coops.coop-kobe.net"]:
for host in ["www.kobe.coop.or.jp"]:
	path2idx("http://%s/" % host)

	while True:
		cur.execute("SELECT * FROM target WHERE host=? AND body IS NULL", (host,))
		target = cur.fetchone()
		if target is None:
			break
		
		idx = target["idx"]
		base = target["url"]
		agent.get(base)
		cur.execute("UPDATE target SET body=? WHERE idx=?", (agent.page_source, idx))
		hrefs = [p.get_attribute("href") for p in agent.find_elements_by_tag_name("a")]
		
		href2 = []
		for href in hrefs:
			if href is None:
				continue
			
			if href.startswith("#"):
				continue
			
			if href.startswith("tel:"):
				continue
			
			if re.match(r"\.(gif|png|jpg|pdf)$", href, re.I):
				continue
			
			href = urljoin(base, href)
			idx2 = path2idx(href)
			cur.execute("INSERT OR IGNORE INTO di VALUES(?,?)", (idx, idx2))
			href2.append(href)
		db.commit()

