import networkx
import sqlite3
import pandas as pd
from urllib.parse import urljoin, urlparse, urlunparse

db = sqlite3.connect("coop.db")
db.row_factory = sqlite3.Row
cur = db.cursor()

def target2url(t):
	parts = [t[i] for i in ("scheme", "netloc", "path", "params", "query")]
	return urlunparse(parts+[""])

idxset = set()
g = networkx.DiGraph()
cur.execute("SELECT * FROM target WHERE internal=1")
for row in cur:
	g.add_node(row["idx"], url=target2url(row))
	idxset.add(row["idx"])

cur.execute("SELECT * FROM target WHERE internal=1 AND jump IS NOT NULL")
for row in cur:
	if row["jump"] in idxset:
		g.add_edge(row["idx"], row["jump"])

cur.execute("SELECT * FROM di")
for row in cur:
	if row["src"] in idxset and row["dst"] in idxset:
		g.add_edge(row["src"], row["dst"])

pr = networkx.pagerank(g, alpha=0.9)

cur.execute("SELECT * FROM target ORDER BY idx")
u=pd.Series({ w["idx"]:target2url(w) for w in cur })
w=(pd.concat([pd.Series(pr), u], axis=1)).sort_values(by=0, ascending=False)
x=w.dropna()
#print(pr)
print(x)
x.to_csv("coop_pagerank.csv")
