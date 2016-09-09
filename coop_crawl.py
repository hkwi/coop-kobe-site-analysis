# coding: UTF-8

import re
import sqlite3
from urllib.parse import urljoin, urlparse, parse_qsl, urlunparse
import selenium.webdriver
import datetime
# XXX: javascript:void() も通過させられる crawler があるといい

db = sqlite3.connect("coop.db")
db.row_factory = sqlite3.Row
cur = db.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS prefix (
	idx INTEGER PRIMARY KEY AUTOINCREMENT,
	netloc VARCHAR(255),
	path VARCHAR(255)
)''')
cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS prefix_url
	ON prefix(netloc,path)''')
cur.execute('''CREATE TABLE IF NOT EXISTS target (
	idx INTEGER PRIMARY KEY AUTOINCREMENT,
	depth INTEGER DEFAULT 0,
	internal BOOL,
	scheme VARCHAR(16),
	netloc VARCHAR(32),
	path VARCHAR(255) DEFAULT "",
	params VARCHAR(255) DEFAULT "",
	query VARCHAR(255) DEFAULT "",
	atime DATETIME,
	alert BOOL,
	jump INTEGER
)''')
cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS target_url
	ON target(scheme,netloc,path,params,query)''')
cur.execute('''CREATE TABLE IF NOT EXISTS di(src INTEGER, dst INTEGER)''')
cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS uniq_di ON di(src, dst)''')

cur.execute("SELECT * FROM prefix")
prefix_all = [r for r in cur.fetchall()]
def is_internal(url):
	p = urlparse(url)
	internal = False
	for r in prefix_all:
		if p.netloc != r["netloc"]:
			continue
		if r["path"] is None:
			internal = True
		elif p.path.startswith(r["path"]):
			internal = True
	return internal

cur.execute("SELECT * FROM target")
for t in cur.fetchall():
	parts = [t[i] for i in ("scheme", "netloc", "path", "params", "query")]
	internal = is_internal(urlunparse(parts+[""]))
	if bool(t["internal"]) != internal:
		cur.execute("UPDATE target SET atime=NULL, internal=? WHERE idx=?", (internal,t["idx"]))
		db.commit()

def url2idx(url, depth):
	p = urlparse(url)
	def fetch():
		cur.execute('''SELECT idx FROM target
			WHERE scheme=? AND netloc=? AND path=? AND params=? AND query=?''', p[:5])
		return cur.fetchone()
	
	r = fetch()
	while r is None:
		try:
			cur.execute('''INSERT INTO target(depth,internal,scheme,netloc,path,params,query)
				VALUES(?,?,?,?,?,?,?)''', (depth, is_internal(url))+p[:5])
			db.commit()
			r = fetch()
		except sqlite3.OperationalError:
			pass
	
	return r["idx"]


profile = selenium.webdriver.FirefoxProfile();
path = "D:\\Downloads_sel";
profile.set_preference("browser.download.folderList", 2);
profile.set_preference("browser.download.dir", path);
profile.set_preference("browser.download.alertOnEXEOpen", False);
profile.set_preference("browser.helperApps.neverAsksaveToDisk", "application/x-msexcel,application/excel,application/x-excel,application/excel,application/x-excel,application/excel,application/vnd.ms-excel,application/x-excel,application/x-msexcel");
profile.set_preference("browser.download.manager.showWhenStarting", False);
profile.set_preference("browser.download.manager.focusWhenStarting", False);
profile.set_preference("browser.helperApps.alwaysAsk.force", False);
profile.set_preference("browser.download.manager.alertOnEXEOpen", False);
profile.set_preference("browser.download.manager.closeWhenDone", False);
profile.set_preference("browser.download.manager.showAlertOnComplete", False);
profile.set_preference("browser.download.manager.useWindow", False);
profile.set_preference("browser.download.manager.showWhenStarting", False);
profile.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False);
profile.set_preference("pdfjs.disabled", True);

#firefoxProfile = selenium.webdriver.firefox.options.FirefoxProfile()
#firefoxProfile.set_preference('permissions.default.image', 2)
#firefoxProfile.set_preference("browser.migration.version", 9999)

agent = selenium.webdriver.Firefox(profile)

depth = 0
while True:
	cur.execute("SELECT MAX(depth) FROM target")
	dmax = cur.fetchone()
	if dmax[0] is None or depth > dmax[0]:
		break
	
	cur.execute('''SELECT * FROM target WHERE depth=?
		AND atime IS NULL AND internal=?
		ORDER BY RANDOM() LIMIT 1''', (depth,True))
	t = cur.fetchone()
	if t is None:
		depth+=1
		continue
	
	idx = t["idx"]
	parts = [t[i] for i in ("scheme", "netloc", "path", "params", "query")]
	base_url = urlunparse(parts+[""])
	agent.get(base_url)
	
	atime = datetime.datetime.now()
	
	if agent.current_url != base_url:
		jump = url2idx(agent.current_url, depth)
		cur.execute("UPDATE target SET atime=?, jump=? WHERE idx=?", (atime,jump,idx))
		idx = jump
		base_url = agent.current_url
	
	alert = False
	try:
		agent.switch_to_alert().accept();
		alert = True
	except:
		pass
	
	ids = []
	hrefs = [p.get_attribute("href") for p in agent.find_elements_by_tag_name("a")]
	for href in hrefs:
		if href is None:
			continue
		
		if href.startswith("#"):
			continue
		
		if href.startswith("tel:"):
			continue
		
		if re.search(r"\.(gif|png|jpg|pdf|ppt|pptx|doc|docx)$", href, re.I):
			continue
		
		href = urljoin(base_url, href)
		p = urlparse(href)
		
		def qs_num(param):
			return int(dict(parse_qsl(p.query)).get(param, "0"))
		
		# 自動生成される URL で、内容が存在しないことが分かっている
		if p.netloc=="ck.coop-kobe.net":
			if p.path=="/kurashi/column/archives.php" and qs_num("p") > 25:
				continue
			if p.path=="/kurashi/food_eco/archives.php" and qs_num("p") > 37:
				continue
			if p.path=="/kurashi/food_eco/eco_note/archives.php" and qs_num("p") > 3:
				continue
			if p.path=="/kurashi/food_eco/food_study/archives.php" and qs_num("p") > 18:
				continue
			if p.path=="/kurashi/food_eco/kids_chromato/archives.php" and qs_num("p") > 2:
				continue
			if p.path=="/kurashi/food_eco/shokuiku_kouza/archives.php" and qs_num("p") > 14:
				continue
			if p.path=="/kurashi/info_net/archives.php" and qs_num("p") > 4:
				continue
			if p.path=="/kurashi/life/archives.php" and qs_num("p") > 9:
				continue
			if p.path=="/kurashi/life/eco_cleanup/archives.php" and qs_num("p") > 5:
				continue
			if p.path=="/kurashi/life/seasonal/archives.php" and qs_num("p") > 3:
				continue
			if p.path=="/kurashi/oshirase/index.php" and qs_num("p") > 2:
				continue
		
		idx2 = url2idx(href, depth+1)
		if idx != idx2:
			ids.append(idx2)
	
	for x in range(5):
		try:
			for idx2 in ids:
				cur.execute("INSERT OR IGNORE INTO di VALUES(?,?)", (idx, idx2))
			cur.execute("UPDATE target SET atime=?, alert=? WHERE idx=?", (atime,alert,idx))
			db.commit()
			break
		except sqlite3.OperationalError:
			pass
