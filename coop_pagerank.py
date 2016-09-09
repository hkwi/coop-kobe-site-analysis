import networkx
import sqlite3
import pandas as pd
from urllib.parse import urljoin, urlparse, parse_qsl

netloc=["www.coop-kobe.net"]
#netloc=["www.kobe.coop.or.jp", "ck.coop-kobe.net"]
#netloc=["www.kobe.coop.or.jp"]
#netloc=["ck.coop-kobe.net"]
#netloc=None

db = sqlite3.connect("coop.db")
db.row_factory = sqlite3.Row
cur = db.cursor()

idxset = set()
g = networkx.DiGraph()
cur.execute("SELECT * FROM target")
for row in cur.fetchall():
	if netloc and urlparse(row["url"]).netloc not in netloc:
		continue
	g.add_node(row["idx"], url=row["url"])
	idxset.add(row["idx"])

cur.execute("SELECT * FROM di")
for row in cur.fetchall():
	if row["src"] in idxset and row["dst"] in idxset:
		g.add_edge(row["src"], row["dst"])

pr = networkx.pagerank(g, alpha=0.9)

cur.execute("SELECT * FROM target ORDER BY idx")
u=pd.Series({ w["idx"]:w["url"] for w in cur.fetchall() })
w=(pd.concat([pd.Series(pr), u], axis=1)).sort_values(by=0, ascending=False)
w.dropna()
#print(pr)
print(w)
