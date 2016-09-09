import re
import sqlite3
from urllib.parse import urlparse, parse_qsl

db = sqlite3.connect("coop.db")
db.row_factory = sqlite3.Row
cur = db.cursor()
cur.execute("SELECT idx,url FROM target")

for row in list(cur.fetchall()):
	href = row["url"]
	p = urlparse(href)
	
	def qs_num(param):
		return int(dict(parse_qsl(p.query)).get(param, "0"))
	
	def purge():
		cur.execute("DELETE FROM di WHERE src=? OR dst=?", (row["idx"], row["idx"]))
		cur.execute("DELETE FROM target WHERE idx=?", (row["idx"],))
		db.commit()
	
	if re.search(r"\.(gif|png|jpg|pdf|ppt)$", href, re.I):
		purge()

	if p.netloc=="ck.coop-kobe.net":
		if p.path=="/kurashi/column/archives.php" and qs_num("p") > 25:
			purge()
		if p.path=="/kurashi/food_eco/archives.php" and qs_num("p") > 37:
			purge()
		if p.path=="/kurashi/food_eco/eco_note/archives.php" and qs_num("p") > 3:
			purge()
		if p.path=="/kurashi/food_eco/food_study/archives.php" and qs_num("p") > 18:
			purge()
		if p.path=="/kurashi/food_eco/kids_chromato/archives.php" and qs_num("p") > 2:
			purge()
		if p.path=="/kurashi/food_eco/shokuiku_kouza/archives.php" and qs_num("p") > 14:
			purge()
		if p.path=="/kurashi/info_net/archives.php" and qs_num("p") > 4:
			purge()
		if p.path=="/kurashi/life/archives.php" and qs_num("p") > 9:
			purge()
		if p.path=="/kurashi/life/eco_cleanup/archives.php" and qs_num("p") > 5:
			purge()
		if p.path=="/kurashi/life/seasonal/archives.php" and qs_num("p") > 3:
			purge()
		if p.path=="/kurashi/oshirase/index.php" and qs_num("p") > 2:
			purge()
