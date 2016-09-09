# coding: UTF-8

import re
import sqlite3
from urllib.parse import urljoin, urlparse, parse_qsl
import selenium.webdriver
# XXX: javascript:void() も通過させられる crawler があるといい

db = sqlite3.connect("coop.db")
db.row_factory = sqlite3.Row
cur = db.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS target (
	idx INTEGER PRIMARY KEY AUTOINCREMENT,
	url VARCHAR(255),
	host VARCHAR(255),
	body TEXT,
	alert BOOL
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

firefoxProfile = selenium.webdriver.firefox.options.FirefoxProfile()
#firefoxProfile.set_preference('permissions.default.image', 2)
#firefoxProfile.set_preference("browser.migration.version", 9999)

agent = selenium.webdriver.Firefox(firefoxProfile)



#for s in ["www.coop-kobe.net", "www.kobe.coop.or.jp", "ck.coop-kobe.net", "coops.coop-kobe.net"]:
for host in ["www.coop-moving.co.jp","www.coop-assis.co.jp","www.coop-net-station.net","www.coop-bakery.co.jp","www.coop-rice-center.co.jp","www.coopfoods.co.jp","eco.coop-kobe.net","office.coop-kobe.net","blog.coop-kobe.net","shohin.coop-kobe.net","topics.coop-kobe.net","mytable.coop-kobe.net","netsuper.coop-kobe.net","tenanto.coop-kobe.net","maikuru.coop-kobe.net","heiwa.coop-kobe.net","bell.coop-kobe.net","fukushi.coop-kobe.net","www.kobe.coop.or.jp","ck.coop-kobe.net", "www.coop-kobe.net","community.coop-kobe.net","coops.coop-kobe.net","cooking.coop-kobe.net","shop.coop-kobe.net","event.coop-kobe.net","kensa.coop-kobe.net","coop-moving-jobs.net","coop-kobe-jobs.net",]:
	path2idx("http://%s/" % host)

	while True:
		cur.execute("SELECT * FROM target WHERE host=? AND body IS NULL ORDER BY RANDOM()", (host,))
		target = cur.fetchone()
		if target is None:
			break
		
		idx = target["idx"]
		base = target["url"]
		agent.get(base)
		try:
			agent.switch_to_alert().accept();
			cur.execute("UPDATE target SET alert=1 WHERE idx=?", (idx,))
		except:
			pass
		
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
			
			if re.search(r"\.(gif|png|jpg|pdf|ppt)$", href, re.I):
				continue
			
			href = urljoin(base, href)
			p = urlparse(href)
			
			def qs_num(param):
				return int(dict(parse_qsl(p.query)).get(param, "0"))
			
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
			
			# 以下は自動生成に近い、大量にページが存在するパターン
			if p.netloc=="www.coop-kobe.net":
				if p.path.startswith("/ec/shop/g/"):
					# アイテム単位画面
					continue
				elif p.path.startswith("/ec/shop/c/"):
					# アイテム一覧画面
					continue
				elif p.path.startswith("/ec/shop/e/"):
					# アイテム一覧画面
					continue
				elif p.path=="/member/shop/goods/webselection.aspx":
					continue
				elif p.path=="/ec/shop/intro/intro.aspx":
					# 入会・ログイン画面
					continue
				elif p.path=="/member/shop/members/blog_form.aspx":
					continue
				elif p.path=="/member/shop/goods/webctlg_accesslink.aspx":
					continue
				elif p.path=="/member/shop/members/seerdrug_request.aspx":
					continue
				elif p.path=="/member/shop/barrierfree/sample.aspx":
					continue
				elif re.match(r"/member/shop/secure/coop_culture\d+.aspx", p.path):
					continue
			elif p.netloc=="www.kobe.coop.or.jp":
				if p.path.startswith("/kouza/detail/"):
					continue
				elif p.path=="/kouza/contact/hyogo.php":
					continue
			elif p.netloc=="community.coop-kobe.net":
				if re.match(r"/odekake/comment/form\d+.html", p.path):
					continue
				elif p.path.startswith("/shokutaku/"):
					continue
			elif p.netloc=="fukushi.coop-kobe.net":
				if re.match(r"/\d{4}/\d{2}/post-\d+.php", p.path):
					continue
			elif p.netloc=="shohin.coop-kobe.net":
				if p.path=="/search/DispDetail_00.do":
					continue
			elif p.netloc=="topics.coop-kobe.net":
				if re.match(r"/\d{4}/\d{2}/", p.path):
					continue
			elif p.netloc in ("coop-kobe-jobs.net","coop-moving-jobs.net"):
				if p.path=="/jobfind-pc/area/All":
					continue
				elif re.match(r"/jobfind-pc/job/All/\d+", p.path):
					continue
			
			idx2 = path2idx(href)
			cur.execute("INSERT OR IGNORE INTO di VALUES(?,?)", (idx, idx2))
			href2.append(href)
		db.commit()

